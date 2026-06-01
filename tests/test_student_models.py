"""Unit tests for Student data models."""

import pytest
from datetime import datetime
from uuid import UUID

from pydantic import ValidationError

from src.models.student import (
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentInDB,
    StudentResponse,
    StudentListResponse,
    StudentDB,
)


class TestStudentBase:
    """Tests for StudentBase model."""
    
    def test_valid_student_base(self):
        """Test creating a valid StudentBase."""
        student = StudentBase(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        assert student.full_name == "John Doe"
        assert student.age == 15
        assert student.class_ == "10A"
        assert student.gender == "Male"
    
    def test_full_name_required(self):
        """Test that full_name is required."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(age=15, class_="10A", gender="Male")
        assert "full_name" in str(exc_info.value)
    
    def test_full_name_empty_string(self):
        """Test that full_name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="", age=15, class_="10A", gender="Male")
        assert "full_name" in str(exc_info.value)
    
    def test_full_name_max_length(self):
        """Test that full_name respects max length."""
        long_name = "A" * 101
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name=long_name, age=15, class_="10A", gender="Male")
        assert "full_name" in str(exc_info.value)
    
    def test_age_required(self):
        """Test that age is required."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", class_="10A", gender="Male")
        assert "age" in str(exc_info.value)
    
    def test_age_minimum_boundary(self):
        """Test that age must be at least 4."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=3, class_="10A", gender="Male")
        assert "age" in str(exc_info.value)
    
    def test_age_maximum_boundary(self):
        """Test that age cannot exceed 25."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=26, class_="10A", gender="Male")
        assert "age" in str(exc_info.value)
    
    def test_age_valid_boundaries(self):
        """Test that age accepts valid boundary values."""
        student_min = StudentBase(full_name="John Doe", age=4, class_="10A", gender="Male")
        assert student_min.age == 4
        
        student_max = StudentBase(full_name="John Doe", age=25, class_="10A", gender="Male")
        assert student_max.age == 25
    
    def test_class_required(self):
        """Test that class_ is required."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=15, gender="Male")
        assert "class_" in str(exc_info.value)
    
    def test_class_empty_string(self):
        """Test that class_ cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=15, class_="", gender="Male")
        assert "class_" in str(exc_info.value)
    
    def test_class_max_length(self):
        """Test that class_ respects max length."""
        long_class = "A" * 21
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=15, class_=long_class, gender="Male")
        assert "class_" in str(exc_info.value)
    
    def test_gender_required(self):
        """Test that gender is required."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(full_name="John Doe", age=15, class_="10A")
        assert "gender" in str(exc_info.value)
    
    def test_gender_valid_values(self):
        """Test that gender accepts valid values."""
        for gender in ["Male", "Female", "Other"]:
            student = StudentBase(
                full_name="John Doe",
                age=15,
                class_="10A",
                gender=gender
            )
            assert student.gender == gender
    
    def test_gender_invalid_value(self):
        """Test that gender rejects invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            StudentBase(
                full_name="John Doe",
                age=15,
                class_="10A",
                gender="Unknown"
            )
        assert "gender" in str(exc_info.value)


class TestStudentCreate:
    """Tests for StudentCreate model."""
    
    def test_student_create_inherits_validation(self):
        """Test that StudentCreate inherits validation from StudentBase."""
        student = StudentCreate(
            full_name="Jane Doe",
            age=16,
            class_="11B",
            gender="Female"
        )
        assert student.full_name == "Jane Doe"
        assert student.age == 16
        assert student.class_ == "11B"
        assert student.gender == "Female"
    
    def test_student_create_validation_error(self):
        """Test that StudentCreate validates data."""
        with pytest.raises(ValidationError):
            StudentCreate(
                full_name="Jane Doe",
                age=30,  # Invalid: exceeds max age
                class_="11B",
                gender="Female"
            )


class TestStudentUpdate:
    """Tests for StudentUpdate model."""
    
    def test_all_fields_optional(self):
        """Test that all fields are optional in StudentUpdate."""
        update = StudentUpdate()
        assert update.full_name is None
        assert update.age is None
        assert update.class_ is None
        assert update.gender is None
    
    def test_partial_update_single_field(self):
        """Test updating a single field."""
        update = StudentUpdate(full_name="Updated Name")
        assert update.full_name == "Updated Name"
        assert update.age is None
        assert update.class_ is None
        assert update.gender is None
    
    def test_partial_update_multiple_fields(self):
        """Test updating multiple fields."""
        update = StudentUpdate(
            full_name="Updated Name",
            age=18,
            gender="Female"
        )
        assert update.full_name == "Updated Name"
        assert update.age == 18
        assert update.gender == "Female"
        assert update.class_ is None
    
    def test_update_validation_on_provided_fields(self):
        """Test that validation applies to provided fields."""
        with pytest.raises(ValidationError):
            StudentUpdate(age=30)  # Invalid age
    
    def test_update_gender_validation(self):
        """Test gender validation in update."""
        with pytest.raises(ValidationError):
            StudentUpdate(gender="Invalid")
    
    def test_update_class_validation(self):
        """Test class validation in update."""
        with pytest.raises(ValidationError):
            StudentUpdate(class_="")  # Empty class


class TestStudentInDB:
    """Tests for StudentInDB model."""
    
    def test_student_in_db_with_defaults(self):
        """Test creating StudentInDB with default values."""
        student = StudentInDB(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        assert student.full_name == "John Doe"
        assert student.age == 15
        assert student.class_ == "10A"
        assert student.gender == "Male"
        assert isinstance(student.id, UUID)
        assert isinstance(student.created_at, datetime)
        assert isinstance(student.updated_at, datetime)
        assert student.deleted_at is None
    
    def test_student_in_db_with_explicit_id(self):
        """Test creating StudentInDB with explicit ID."""
        from uuid import uuid4
        test_id = uuid4()
        student = StudentInDB(
            id=test_id,
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        assert student.id == test_id
    
    def test_student_in_db_with_deleted_at(self):
        """Test StudentInDB with deleted_at timestamp."""
        now = datetime.utcnow()
        student = StudentInDB(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male",
            deleted_at=now
        )
        assert student.deleted_at == now


class TestStudentResponse:
    """Tests for StudentResponse model."""
    
    def test_student_response_inherits_from_in_db(self):
        """Test that StudentResponse inherits from StudentInDB."""
        student = StudentResponse(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        assert isinstance(student, StudentInDB)
        assert student.full_name == "John Doe"


class TestStudentListResponse:
    """Tests for StudentListResponse model."""
    
    def test_empty_list_response(self):
        """Test creating an empty list response."""
        response = StudentListResponse(
            students=[],
            total=0,
            page=1,
            page_size=20,
            total_pages=0
        )
        assert response.students == []
        assert response.total == 0
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 0
    
    def test_list_response_with_students(self):
        """Test creating a list response with students."""
        student1 = StudentResponse(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        student2 = StudentResponse(
            full_name="Jane Doe",
            age=16,
            class_="11B",
            gender="Female"
        )
        
        response = StudentListResponse(
            students=[student1, student2],
            total=2,
            page=1,
            page_size=20,
            total_pages=1
        )
        assert len(response.students) == 2
        assert response.total == 2
        assert response.total_pages == 1


class TestStudentDB:
    """Tests for StudentDB SQLAlchemy model."""
    
    def test_student_db_creation(self):
        """Test creating a StudentDB instance."""
        student = StudentDB(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        assert student.full_name == "John Doe"
        assert student.age == 15
        assert student.class_ == "10A"
        assert student.gender == "Male"
        assert isinstance(student.id, UUID)
    
    def test_student_db_to_pydantic(self):
        """Test converting StudentDB to Pydantic model."""
        student_db = StudentDB(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        student_pydantic = student_db.to_pydantic()
        
        assert isinstance(student_pydantic, StudentInDB)
        assert student_pydantic.full_name == "John Doe"
        assert student_pydantic.age == 15
        assert student_pydantic.class_ == "10A"
        assert student_pydantic.gender == "Male"
    
    def test_student_db_from_pydantic(self):
        """Test creating StudentDB from Pydantic model."""
        student_create = StudentCreate(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        student_db = StudentDB.from_pydantic(student_create)
        
        assert student_db.full_name == "John Doe"
        assert student_db.age == 15
        assert student_db.class_ == "10A"
        assert student_db.gender == "Male"
    
    def test_student_db_table_name(self):
        """Test that StudentDB uses correct table name."""
        assert StudentDB.__tablename__ == 'students'
    
    def test_student_db_column_mapping(self):
        """Test that StudentDB columns are correctly mapped."""
        assert hasattr(StudentDB, 'id')
        assert hasattr(StudentDB, 'full_name')
        assert hasattr(StudentDB, 'age')
        assert hasattr(StudentDB, 'class_')
        assert hasattr(StudentDB, 'gender')
        assert hasattr(StudentDB, 'created_at')
        assert hasattr(StudentDB, 'updated_at')
        assert hasattr(StudentDB, 'deleted_at')


class TestValidationRules:
    """Tests for validation rules across models."""
    
    def test_full_name_validation_consistency(self):
        """Test that full_name validation is consistent across models."""
        valid_name = "John Doe"
        
        # Should work in StudentBase
        base = StudentBase(full_name=valid_name, age=15, class_="10A", gender="Male")
        assert base.full_name == valid_name
        
        # Should work in StudentCreate
        create = StudentCreate(full_name=valid_name, age=15, class_="10A", gender="Male")
        assert create.full_name == valid_name
        
        # Should work in StudentUpdate
        update = StudentUpdate(full_name=valid_name)
        assert update.full_name == valid_name
    
    def test_age_validation_consistency(self):
        """Test that age validation is consistent across models."""
        valid_age = 15
        
        # Should work in StudentBase
        base = StudentBase(full_name="John Doe", age=valid_age, class_="10A", gender="Male")
        assert base.age == valid_age
        
        # Should work in StudentCreate
        create = StudentCreate(full_name="John Doe", age=valid_age, class_="10A", gender="Male")
        assert create.age == valid_age
        
        # Should work in StudentUpdate
        update = StudentUpdate(age=valid_age)
        assert update.age == valid_age
    
    def test_gender_validation_consistency(self):
        """Test that gender validation is consistent across models."""
        for gender in ["Male", "Female", "Other"]:
            # Should work in StudentBase
            base = StudentBase(full_name="John Doe", age=15, class_="10A", gender=gender)
            assert base.gender == gender
            
            # Should work in StudentCreate
            create = StudentCreate(full_name="John Doe", age=15, class_="10A", gender=gender)
            assert create.gender == gender
            
            # Should work in StudentUpdate
            update = StudentUpdate(gender=gender)
            assert update.gender == gender
    
    def test_class_validation_consistency(self):
        """Test that class validation is consistent across models."""
        valid_class = "10A"
        
        # Should work in StudentBase
        base = StudentBase(full_name="John Doe", age=15, class_=valid_class, gender="Male")
        assert base.class_ == valid_class
        
        # Should work in StudentCreate
        create = StudentCreate(full_name="John Doe", age=15, class_=valid_class, gender="Male")
        assert create.class_ == valid_class
        
        # Should work in StudentUpdate
        update = StudentUpdate(class_=valid_class)
        assert update.class_ == valid_class


class TestModelSerialization:
    """Tests for model serialization and deserialization."""
    
    def test_student_response_json_serialization(self):
        """Test that StudentResponse can be serialized to JSON."""
        student = StudentResponse(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        json_data = student.model_dump_json()
        assert isinstance(json_data, str)
        assert "John Doe" in json_data
        assert "15" in json_data
    
    def test_student_response_dict_conversion(self):
        """Test that StudentResponse can be converted to dict."""
        student = StudentResponse(
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male"
        )
        data = student.model_dump()
        assert isinstance(data, dict)
        assert data["full_name"] == "John Doe"
        assert data["age"] == 15
        assert data["class_"] == "10A"
        assert data["gender"] == "Male"
