"""Student service implementation for the School Management System."""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from pydantic import ValidationError

from ..models.student import (
    StudentCreate,
    StudentUpdate,
    StudentInDB,
    StudentResponse,
)
from ..repositories.student_repository import StudentRepository


class StudentService:
    """Service layer for student operations with business logic."""
    
    def __init__(self, repository: StudentRepository, enable_duplicate_detection: bool = True):
        """Initialize service with repository and configuration.
        
        Args:
            repository: StudentRepository instance for data access
            enable_duplicate_detection: Whether to prevent duplicate students
        """
        self.repository = repository
        self.enable_duplicate_detection = enable_duplicate_detection
    
    async def create_student(self, student_data: StudentCreate) -> StudentInDB:
        """Create a new student record.
        
        Implements business logic for student creation including:
        - Data validation via Pydantic models
        - Duplicate detection (if enabled)
        - Unique ID generation (UUID)
        - Timestamp management
        
        Args:
            student_data: Student data for creation (StudentCreate model)
            
        Returns:
            Created student record with generated ID
            
        Raises:
            ValueError: If student data is invalid or duplicate detected
            Exception: If database operation fails
            
        Validates: Requirements 1.1, 1.2, 1.7
        """
        try:
            # Validate student data (Pydantic validation happens automatically)
            # The StudentCreate model ensures all required fields are present
            # and all validation rules are applied
            
            # Check for duplicates if enabled
            if self.enable_duplicate_detection:
                existing = await self.repository.get_by_criteria({
                    'full_name': student_data.full_name,
                    'class_': student_data.class_,
                })
                if existing:
                    raise ValueError(
                        f"Student with name '{student_data.full_name}' in class "
                        f"'{student_data.class_}' already exists"
                    )
            
            # Create student in repository
            # Repository handles UUID generation and timestamp management
            created_student = await self.repository.create(student_data)
            
            return created_student
            
        except ValueError as e:
            # Re-raise validation and business logic errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise Exception(f"Failed to create student: {str(e)}")
    
    async def get_student(self, student_id: UUID) -> Optional[StudentInDB]:
        """Get a student by ID.
        
        Args:
            student_id: UUID of the student to retrieve
            
        Returns:
            Student record if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            return await self.repository.get_by_id(student_id)
        except Exception as e:
            raise Exception(f"Failed to retrieve student: {str(e)}")
    
    async def get_all_students(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'asc'
    ) -> Tuple[List[StudentInDB], int]:
        """Get all students with optional filtering, sorting, and pagination.
        
        Implements business logic for retrieving students including:
        - Pagination support (skip/limit)
        - Filtering by multiple criteria
        - Sorting by any field
        - Total count for pagination metadata
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Dictionary of filter criteria (e.g., {'class_': '10A', 'gender': 'Male'})
            sort_by: Field to sort by (e.g., 'full_name', 'age', 'created_at')
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (list of students, total count)
            
        Raises:
            ValueError: If pagination parameters are invalid
            Exception: If database operation fails
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        try:
            # Validate pagination parameters
            if skip < 0:
                raise ValueError("skip must be non-negative")
            if limit < 1:
                raise ValueError("limit must be at least 1")
            
            # Validate sort order
            if sort_order.lower() not in ['asc', 'desc']:
                raise ValueError("sort_order must be 'asc' or 'desc'")
            
            # Get students from repository
            students, total = await self.repository.get_all(
                skip=skip,
                limit=limit,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            return students, total
            
        except ValueError as e:
            raise
        except Exception as e:
            raise Exception(f"Failed to retrieve students: {str(e)}")
    
    async def update_student(
        self,
        student_id: UUID,
        update_data: StudentUpdate
    ) -> Optional[StudentInDB]:
        """Update an existing student record.
        
        Implements business logic for student updates including:
        - Partial updates (only provided fields are updated)
        - Data validation via Pydantic models
        - Duplicate detection for name/class changes (if enabled)
        - Timestamp management
        
        Args:
            student_id: UUID of the student to update
            update_data: Student data for update (StudentUpdate model)
            
        Returns:
            Updated student record if found, None if student not found
            
        Raises:
            ValueError: If update data is invalid or duplicate detected
            Exception: If database operation fails
            
        Validates: Requirements 3.1, 3.2, 3.5
        """
        try:
            # Check if student exists
            existing_student = await self.repository.get_by_id(student_id)
            if not existing_student:
                return None
            
            # Check for duplicates if name or class is being updated
            update_dict = update_data.dict(exclude_unset=True)
            if self.enable_duplicate_detection and ('full_name' in update_dict or 'class_' in update_dict):
                new_name = update_dict.get('full_name', existing_student.full_name)
                new_class = update_dict.get('class_', existing_student.class_)
                
                # Only check if values are actually changing
                if new_name != existing_student.full_name or new_class != existing_student.class_:
                    existing_with_new_criteria = await self.repository.get_by_criteria({
                        'full_name': new_name,
                        'class_': new_class,
                    })
                    if existing_with_new_criteria:
                        raise ValueError(
                            f"Student with name '{new_name}' in class '{new_class}' already exists"
                        )
            
            # Update student in repository
            updated_student = await self.repository.update(student_id, update_data)
            
            return updated_student
            
        except ValueError as e:
            raise
        except Exception as e:
            raise Exception(f"Failed to update student: {str(e)}")
    
    async def delete_student(
        self,
        student_id: UUID,
        soft_delete: bool = True
    ) -> bool:
        """Delete a student record.
        
        Implements business logic for student deletion including:
        - Soft delete support (mark as deleted instead of hard delete)
        - Timestamp management for soft deletes
        
        Args:
            student_id: UUID of the student to delete
            soft_delete: If True, mark as deleted; if False, hard delete
            
        Returns:
            True if deleted, False if student not found
            
        Raises:
            Exception: If database operation fails
            
        Validates: Requirements 4.1, 4.2, 4.4
        """
        try:
            # Delete student in repository
            deleted = await self.repository.delete(student_id, soft_delete=soft_delete)
            
            return deleted
            
        except Exception as e:
            raise Exception(f"Failed to delete student: {str(e)}")
    
    async def validate_student_data(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate student data against business rules.
        
        Validates student data including:
        - Required fields presence
        - Data type validation
        - Field-specific validation rules
        - Business rule validation
        
        Args:
            student_data: Dictionary of student data to validate
            
        Returns:
            Dictionary with validation result:
            {
                'valid': bool,
                'errors': List[Dict] with field and message
            }
            
        Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
        """
        errors = []
        
        try:
            # Try to create StudentCreate model to validate
            StudentCreate(**student_data)
            return {'valid': True, 'errors': []}
        except ValidationError as e:
            # Extract validation errors
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                message = error['msg']
                errors.append({
                    'field': str(field),
                    'message': message
                })
            
            return {'valid': False, 'errors': errors}
    
    async def check_duplicate_student(
        self,
        full_name: str,
        class_: str,
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Check if a student with the same name and class exists.
        
        Args:
            full_name: Student's full name
            class_: Student's class
            exclude_id: Optional student ID to exclude from check (for updates)
            
        Returns:
            True if duplicate exists, False otherwise
        """
        if not self.enable_duplicate_detection:
            return False
        
        try:
            existing = await self.repository.get_by_criteria({
                'full_name': full_name,
                'class_': class_,
            })
            
            if not existing:
                return False
            
            # If exclude_id is provided, check if the found student is different
            if exclude_id:
                return any(student.id != exclude_id for student in existing)
            
            return len(existing) > 0
            
        except Exception as e:
            raise Exception(f"Failed to check for duplicates: {str(e)}")
    
    async def get_students_by_class(self, class_: str) -> List[StudentInDB]:
        """Get all students in a specific class.
        
        Args:
            class_: Class identifier
            
        Returns:
            List of students in the class
        """
        try:
            students, _ = await self.get_all_students(
                limit=1000,  # Large limit to get all students in class
                filters={'class_': class_}
            )
            return students
        except Exception as e:
            raise Exception(f"Failed to retrieve students by class: {str(e)}")
    
    async def get_students_by_gender(self, gender: str) -> List[StudentInDB]:
        """Get all students with a specific gender.
        
        Args:
            gender: Gender value ('Male', 'Female', 'Other')
            
        Returns:
            List of students with the specified gender
        """
        try:
            students, _ = await self.get_all_students(
                limit=1000,  # Large limit to get all students with gender
                filters={'gender': gender}
            )
            return students
        except Exception as e:
            raise Exception(f"Failed to retrieve students by gender: {str(e)}")
    
    async def get_students_by_age_range(self, min_age: int, max_age: int) -> List[StudentInDB]:
        """Get all students within an age range.
        
        Args:
            min_age: Minimum age (inclusive)
            max_age: Maximum age (inclusive)
            
        Returns:
            List of students within the age range
        """
        try:
            students, _ = await self.get_all_students(
                limit=1000,  # Large limit to get all students in age range
                filters={'age': [min_age, max_age]}
            )
            return students
        except Exception as e:
            raise Exception(f"Failed to retrieve students by age range: {str(e)}")
    
    def set_duplicate_detection(self, enabled: bool) -> None:
        """Enable or disable duplicate detection.
        
        Args:
            enabled: Whether to enable duplicate detection
        """
        self.enable_duplicate_detection = enabled
    
    def is_duplicate_detection_enabled(self) -> bool:
        """Check if duplicate detection is enabled.
        
        Returns:
            True if duplicate detection is enabled, False otherwise
        """
        return self.enable_duplicate_detection
