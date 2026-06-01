"""Student repository implementation for the School Management System."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, update, delete, and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..models.student import StudentDB, StudentCreate, StudentUpdate, StudentInDB


class BaseRepository(ABC):
    """Base repository interface defining common CRUD operations."""
    
    @abstractmethod
    async def create(self, data: Any) -> Any:
        """Create a new record."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[Any]:
        """Get a record by its ID."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get all records with pagination."""
        pass
    
    @abstractmethod
    async def update(self, id: Any, data: Any) -> Optional[Any]:
        """Update a record."""
        pass
    
    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete a record."""
        pass


class StudentRepository(BaseRepository):
    """Repository for student data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def create(self, student_data: StudentCreate) -> StudentInDB:
        """Create a new student record.
        
        Args:
            student_data: Student data for creation
            
        Returns:
            Created student record
            
        Raises:
            ValueError: If student data is invalid
        """
        # Check for duplicates (same full_name and class)
        duplicate_query = select(StudentDB).where(
            and_(
                StudentDB.full_name == student_data.full_name,
                StudentDB.class_ == student_data.class_,
                StudentDB.deleted_at.is_(None)
            )
        )
        duplicate_result = await self.session.execute(duplicate_query)
        if duplicate_result.scalar_one_or_none():
            raise ValueError(f"Student with name '{student_data.full_name}' in class '{student_data.class_}' already exists")
        
        # Create new student
        student_db = StudentDB.from_pydantic(student_data)
        self.session.add(student_db)
        await self.session.commit()
        await self.session.refresh(student_db)
        
        return student_db.to_pydantic()
    
    async def get_by_id(self, student_id: UUID) -> Optional[StudentInDB]:
        """Get a student by ID.
        
        Args:
            student_id: Student UUID
            
        Returns:
            Student record if found, None otherwise
        """
        query = select(StudentDB).where(
            and_(
                StudentDB.id == student_id,
                StudentDB.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        student_db = result.scalar_one_or_none()
        
        return student_db.to_pydantic() if student_db else None
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'asc'
    ) -> Tuple[List[StudentInDB], int]:
        """Get all students with filtering, sorting, and pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Dictionary of filter criteria
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (list of students, total count)
        """
        # Build base query
        query = select(StudentDB).where(StudentDB.deleted_at.is_(None))
        
        # Apply filters
        if filters:
            filter_conditions = []
            for field, value in filters.items():
                if field == 'full_name' and value:
                    filter_conditions.append(StudentDB.full_name.ilike(f"%{value}%"))
                elif field == 'age' and value:
                    if isinstance(value, list) and len(value) == 2:
                        # Age range filter
                        filter_conditions.append(StudentDB.age.between(value[0], value[1]))
                    else:
                        # Exact age filter
                        filter_conditions.append(StudentDB.age == value)
                elif field == 'class_' and value:
                    filter_conditions.append(StudentDB.class_ == value)
                elif field == 'gender' and value:
                    filter_conditions.append(StudentDB.gender == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Apply sorting
        if sort_by:
            sort_field = getattr(StudentDB, sort_by, None)
            if sort_field:
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
            else:
                # Default sorting by created_at descending
                query = query.order_by(desc(StudentDB.created_at))
        else:
            # Default sorting by created_at descending
            query = query.order_by(desc(StudentDB.created_at))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.session.execute(query)
        students_db = result.scalars().all()
        
        # Convert to Pydantic models
        students = [student.to_pydantic() for student in students_db]
        
        return students, total
    
    async def update(self, student_id: UUID, student_data: StudentUpdate) -> Optional[StudentInDB]:
        """Update a student record.
        
        Args:
            student_id: Student UUID
            student_data: Student data for update
            
        Returns:
            Updated student record if found, None otherwise
            
        Raises:
            ValueError: If update data is invalid
        """
        # Get existing student
        query = select(StudentDB).where(
            and_(
                StudentDB.id == student_id,
                StudentDB.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        student_db = result.scalar_one_or_none()
        
        if not student_db:
            return None
        
        # Check for duplicates if name or class is being updated
        update_data = student_data.dict(exclude_unset=True)
        if 'full_name' in update_data or 'class_' in update_data:
            new_name = update_data.get('full_name', student_db.full_name)
            new_class = update_data.get('class_', student_db.class_)
            
            duplicate_query = select(StudentDB).where(
                and_(
                    StudentDB.full_name == new_name,
                    StudentDB.class_ == new_class,
                    StudentDB.id != student_id,
                    StudentDB.deleted_at.is_(None)
                )
            )
            duplicate_result = await self.session.execute(duplicate_query)
            if duplicate_result.scalar_one_or_none():
                raise ValueError(f"Student with name '{new_name}' in class '{new_class}' already exists")
        
        # Update fields
        for field, value in update_data.items():
            if value is not None:
                setattr(student_db, field, value)
        
        # Update timestamp
        student_db.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(student_db)
        
        return student_db.to_pydantic()
    
    async def delete(self, student_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a student record.
        
        Args:
            student_id: Student UUID
            soft_delete: If True, mark as deleted instead of hard delete
            
        Returns:
            True if deleted, False if not found
        """
        if soft_delete:
            # Soft delete - mark as deleted
            query = update(StudentDB).where(
                and_(
                    StudentDB.id == student_id,
                    StudentDB.deleted_at.is_(None)
                )
            ).values(deleted_at=datetime.utcnow())
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            return result.rowcount > 0
        else:
            # Hard delete - remove from database
            query = delete(StudentDB).where(StudentDB.id == student_id)
            
            result = await self.session.execute(query)
            await self.session.commit()
            
            return result.rowcount > 0
    
    async def exists_by_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Check if a student exists matching the given criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            True if at least one student matches, False otherwise
        """
        conditions = [StudentDB.deleted_at.is_(None)]
        
        for field, value in criteria.items():
            if hasattr(StudentDB, field):
                conditions.append(getattr(StudentDB, field) == value)
        
        query = select(func.count()).select_from(StudentDB).where(and_(*conditions))
        result = await self.session.execute(query)
        count = result.scalar()
        
        return count > 0
    
    async def get_by_criteria(self, criteria: Dict[str, Any]) -> List[StudentInDB]:
        """Get students matching the given criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching student records
        """
        conditions = [StudentDB.deleted_at.is_(None)]
        
        for field, value in criteria.items():
            if hasattr(StudentDB, field):
                conditions.append(getattr(StudentDB, field) == value)
        
        query = select(StudentDB).where(and_(*conditions))
        result = await self.session.execute(query)
        students_db = result.scalars().all()
        
        return [student.to_pydantic() for student in students_db]
    
    async def bulk_create(self, students_data: List[StudentCreate]) -> List[StudentInDB]:
        """Create multiple student records in a single transaction.
        
        Args:
            students_data: List of student data for creation
            
        Returns:
            List of created student records
            
        Raises:
            ValueError: If any student data is invalid
        """
        students_db = []
        for student_data in students_data:
            student_db = StudentDB.from_pydantic(student_data)
            students_db.append(student_db)
        
        self.session.add_all(students_db)
        await self.session.commit()
        
        # Refresh all students to get their IDs
        for student_db in students_db:
            await self.session.refresh(student_db)
        
        return [student.to_pydantic() for student in students_db]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about students.
        
        Returns:
            Dictionary with student statistics
        """
        # Total active students
        total_query = select(func.count()).where(StudentDB.deleted_at.is_(None))
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()
        
        # Count by gender
        gender_query = select(
            StudentDB.gender,
            func.count().label('count')
        ).where(
            StudentDB.deleted_at.is_(None)
        ).group_by(StudentDB.gender)
        
        gender_result = await self.session.execute(gender_query)
        gender_counts = {row.gender: row.count for row in gender_result}
        
        # Count by class
        class_query = select(
            StudentDB.class_,
            func.count().label('count')
        ).where(
            StudentDB.deleted_at.is_(None)
        ).group_by(StudentDB.class_)
        
        class_result = await self.session.execute(class_query)
        class_counts = {row.class_: row.count for row in class_result}
        
        # Age statistics
        age_query = select(
            func.min(StudentDB.age).label('min_age'),
            func.max(StudentDB.age).label('max_age'),
            func.avg(StudentDB.age).label('avg_age')
        ).where(StudentDB.deleted_at.is_(None))
        
        age_result = await self.session.execute(age_query)
        age_stats = age_result.one()
        
        return {
            'total_students': total,
            'gender_distribution': gender_counts,
            'class_distribution': class_counts,
            'age_statistics': {
                'min': age_stats.min_age,
                'max': age_stats.max_age,
                'average': float(age_stats.avg_age) if age_stats.avg_age else 0.0,
            }
        }


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str):
        """Initialize database manager with connection URL.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = None
        self.async_session_factory = None
    
    async def connect(self):
        """Create database engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def disconnect(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
    
    def get_session(self) -> AsyncSession:
        """Get a new database session.
        
        Returns:
            AsyncSession object
        """
        if not self.async_session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        return self.async_session_factory()
    
    async def create_tables(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(StudentDB.metadata.create_all)
    
    async def drop_tables(self):
        """Drop database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(StudentDB.metadata.drop_all)