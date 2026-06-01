import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .repositories.student_repository import DatabaseManager
from .models.student import StudentDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppConfig:
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/school_db'
    )
    SERVER_HOST: str = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT: int = int(os.getenv('SERVER_PORT', '8000'))
    CORS_ORIGINS: list = [
        'http://localhost',
        'http://localhost:3000',
        'http://localhost:8000',
        'http://127.0.0.1',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8000',
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ['*']
    CORS_ALLOW_HEADERS: list = ['*']
    ENABLE_DUPLICATE_DETECTION: bool = os.getenv('ENABLE_DUPLICATE_DETECTION', 'true').lower() == 'true'
    ENABLE_SOFT_DELETE: bool = os.getenv('ENABLE_SOFT_DELETE', 'true').lower() == 'true'
    API_TITLE: str = 'School Management System API'
    API_VERSION: str = '1.0.0'
    API_DESCRIPTION: str = 'RESTful API for managing student records'


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


db_manager: Optional[DatabaseManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_manager
    
    logger.info("Starting School Management System API")
    logger.info(f"Database URL: {AppConfig.DATABASE_URL}")
    
    try:
        db_manager = DatabaseManager(AppConfig.DATABASE_URL)
        await db_manager.connect()
        logger.info("Database connection established")
        
        await db_manager.create_tables()
        logger.info("Database tables created/verified")
        
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    logger.info("Shutting down School Management System API")
    
    try:
        if db_manager:
            await db_manager.disconnect()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    
    logger.info("Application shutdown completed")


# ============================================================================
# Application Factory
# ============================================================================

def create_app() -> FastAPI:
    app = FastAPI(
        title=AppConfig.API_TITLE,
        description=AppConfig.API_DESCRIPTION,
        version=AppConfig.API_VERSION,
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=AppConfig.CORS_ORIGINS,
        allow_credentials=AppConfig.CORS_ALLOW_CREDENTIALS,
        allow_methods=AppConfig.CORS_ALLOW_METHODS,
        allow_headers=AppConfig.CORS_ALLOW_HEADERS,
    )
    
    @app.middleware("http")
    async def add_request_id_middleware(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        logger.info(f"[{request_id}] Response: {response.status_code}")
        
        return response
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        request_id = getattr(request.state, 'request_id', 'unknown')
        logger.warning(f"[{request_id}] Validation error: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc),
                    "timestamp": datetime.utcnow().isoformat(),
                    "requestId": request_id,
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, 'request_id', 'unknown')
        logger.error(
            f"[{request_id}] Unexpected error: {str(exc)}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "requestId": request_id,
                }
            },
        )
    
    @app.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK, tags=["Health"])
    async def health_check() -> HealthCheckResponse:
        try:
            if not db_manager or not db_manager.engine:
                raise Exception("Database not initialized")
            
            async with db_manager.get_session() as session:
                await session.execute("SELECT 1")
            
            database_status = "connected"
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            database_status = f"error: {str(e)}"
        
        return HealthCheckResponse(
            status="healthy" if database_status == "connected" else "degraded",
            timestamp=datetime.utcnow(),
            version=AppConfig.API_VERSION,
            database=database_status,
        )
    
    @app.get("/", tags=["Root"])
    async def root():
        return {
            "title": AppConfig.API_TITLE,
            "version": AppConfig.API_VERSION,
            "description": AppConfig.API_DESCRIPTION,
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
            },
        }
    
    logger.info("FastAPI application created successfully")
    
    return app


app = create_app()


def get_db_manager() -> DatabaseManager:
    if not db_manager:
        raise RuntimeError("Database manager not initialized")
    return db_manager


async def get_db_session() -> AsyncSession:
    manager = get_db_manager()
    session = manager.get_session()
    try:
        yield session
    finally:
        await session.close()


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {AppConfig.SERVER_HOST}:{AppConfig.SERVER_PORT}")
    
    uvicorn.run(
        "src.main:app",
        host=AppConfig.SERVER_HOST,
        port=AppConfig.SERVER_PORT,
        reload=True,
        log_level="info",
    )
