# School Management System

A production-ready REST API backend for managing student records with comprehensive validation, persistence, and error handling.

## Features

- **Student Management**: Create, read, update, and delete student records
- **Advanced Querying**: Pagination, filtering, and sorting capabilities
- **Data Validation**: Comprehensive input validation with descriptive error messages
- **Soft Delete**: Mark records as deleted without removing data
- **Duplicate Detection**: Prevent duplicate student records
- **API Documentation**: Interactive Swagger UI and ReDoc
- **Error Handling**: Consistent error responses with request tracing
- **Async Support**: Non-blocking database operations
- **Type Safety**: Full type hints throughout codebase

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Validation**: Pydantic 2.5.0
- **ORM**: SQLAlchemy 2.0.23
- **Database**: PostgreSQL with asyncpg
- **Testing**: pytest, pytest-asyncio, hypothesis
- **Python**: 3.8+

## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip or poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Z10N-exe/STUDBACKEND.git
cd school-management-system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Create database:
```bash
createdb school_db
```

## Running

### Start Server
```bash
python -m uvicorn src.main:app --reload
```

Server runs at: `http://localhost:8000`

### Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Run Tests
```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/students` | Create student |
| GET | `/api/students` | List students |
| GET | `/api/students/{id}` | Get student |
| PUT | `/api/students/{id}` | Update student |
| PATCH | `/api/students/{id}` | Partial update |
| DELETE | `/api/students/{id}` | Delete student |

## Usage Examples

### Create Student
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "age": 15,
    "class": "10A",
    "gender": "Male"
  }'
```

### List Students
```bash
curl http://localhost:8000/api/students?skip=0&limit=10
```

### Filter by Class
```bash
curl "http://localhost:8000/api/students?class=10A"
```

### Sort by Age
```bash
curl "http://localhost:8000/api/students?sort_by=age&sort_order=asc"
```

See [USAGE.md](USAGE.md) for more examples.

## Project Structure

```
school-management-system/
├── src/
│   ├── main.py                      # FastAPI application
│   ├── models/
│   │   └── student.py               # Data models
│   ├── repositories/
│   │   └── student_repository.py    # Data access layer
│   ├── services/
│   │   └── student_service.py       # Business logic
│   └── routes/
│       └── students.py              # API endpoints
├── tests/
│   ├── test_student_models.py
│   ├── test_student_service.py
│   └── test_student_validation_properties.py
├── API.md                           # API documentation
├── USAGE.md                         # Usage guide
├── postman_collection.json          # Postman collection
├── pyproject.toml                   # Project configuration
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## Validation Rules

| Field | Rules |
|-------|-------|
| full_name | Required, 1-100 characters |
| age | Required, integer 4-25 |
| class | Required, 1-20 characters |
| gender | Required, one of: Male, Female, Other |

## Error Handling

All errors return consistent JSON format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "timestamp": "ISO-8601 timestamp",
    "requestId": "unique-request-id"
  }
}
```

## Configuration

Environment variables in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/school_db
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENABLE_DUPLICATE_DETECTION=true
ENABLE_SOFT_DELETE=true
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_student_models.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Code Style
Follow PEP 8 guidelines. Use a linter:
```bash
pip install flake8
flake8 src/
```

### Type Checking
```bash
pip install mypy
mypy src/
```

## Deployment

### Production Server
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

### Docker
```bash
docker build -t school-management-system .
docker run -p 8000:8000 school-management-system
```

## API Documentation

- [API Reference](API.md) - Complete endpoint documentation
- [Usage Guide](USAGE.md) - Examples and workflows
- [Postman Collection](postman_collection.json) - Ready-to-import collection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API examples in USAGE.md

## Status

✅ Production Ready
- All core features implemented
- Comprehensive error handling
- Full API documentation
- Test coverage included
