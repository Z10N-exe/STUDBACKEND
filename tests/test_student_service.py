"""Unit and property-based tests for StudentService business logic.

**Validates: Requirements 1.1, 1.2, 1.7, 3.1, 3.2, 4.1, 4.2**
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, assume

from src.models.student import (
    StudentCreate,
    StudentUpdate,
    StudentInDB,
)
from src.services.student_service import StudentService
from src.repositories.student_repository import StudentRepository


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock StudentRepository."""
    return AsyncMock(spec=StudentRepository)


@pytest.fixture
def student_service(mock_repository):
    """Create a StudentService with mock repository."""
    return StudentService(
        repository=mock_repository,
        enable_duplicate_detection=True
    )


@pytest.fixture
def sample_student_data():
    """Create sample student data for testing."""
    return StudentCreate(
        full_name="John Doe",
        age=15,
        class_="10A",
        gender="Male"
    )


@pytest.fixture
def sample_student_in_db():
    """Create a sample StudentInDB object."""
    return StudentInDB(
        id=uuid4(),
        full_name="John Doe",
        age=15,
        class_="10A",
        gender="Male",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# Strategies for property-based testing
valid_full_names = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=100
)

valid_ages = st.integers(min_value=4, max_value=25)

valid_classes = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=20
)

valid_genders = st.sampled_from(['Male', 'Female', 'Other'])


class TestStudentServiceCreation:
    """Tests for student creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_student_success(self, student_service, mock_repository, sample_student_data, sample_student_in_db):
        """Test successful student creation."""
        mock_repository.get_by_criteria.return_value = []
        mock_repository.create.return_value = sample_student_in_db
        
        result = await student_service.create_student(sample_student_data)
        
        assert result.id == sample_student_in_db.id
        assert result.full_name == sample_student_data.full_name
        assert result.age == sample_student_data.age
        assert result.class_ == sample_student_data.class_
        assert result.gender == sample_student_data.gender
        mock_repository.create.assert_called_once_with(sample_student_data)
    
    @pytest.mark.asyncio
    async def test_create_student_with_duplicate_detection_enabled(self, student_service, mock_repository, sample_student_data):
        """Test that duplicate detection prevents duplicate creation."""
        existing_student = StudentInDB(
            id=uuid4(),
            full_name=sample_student_data.full_name,
            age=20,
            class_=sample_student_data.class_,
            gender="Female",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        mock_repository.get_by_criteria.return_value = [existing_student]
        
        with pytest.raises(ValueError) as exc_info:
            await student_service.create_student(sample_student_data)
        
        assert "already exists" in str(exc_info.value)
        mock_repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_student_with_duplicate_detection_disabled(self, mock_repository, sample_student_data, sample_student_in_db):
        """Test that duplicate detection can be disabled."""
        service = StudentService(repository=mock_repository, enable_duplicate_detection=False)
        mock_repository.create.return_value = sample_student_in_db
        
        result = await service.create_student(sample_student_data)
        
        assert result.id == sample_student_in_db.id
        mock_repository.get_by_criteria.assert_not_called()
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_student_generates_unique_id(self, student_service, mock_repository, sample_student_data):
        """Test that created students have unique IDs."""
        student1_id = uuid4()
        student2_id = uuid4()
        
        student1 = StudentInDB(
            id=student1_id,
            full_name=sample_student_data.full_name,
            age=sample_student_data.age,
            class_=sample_student_data.class_,
            gender=sample_student_data.gender,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        student2 = StudentInDB(
            id=student2_id,
            full_name="Jane Doe",
            age=16,
            class_="11B",
            gender="Female",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        mock_repository.get_by_criteria.return_value = []
        mock_repository.create.side_effect = [student1, student2]
        
        result1 = await student_service.create_student(sample_student_data)
        result2 = await student_service.create_student(
            StudentCreate(full_name="Jane Doe", age=16, class_="11B", gender="Female")
        )
        
        assert result1.id != result2.id
        assert isinstance(result1.id, UUID)
        assert isinstance(result2.id, UUID)
    
    @pytest.mark.asyncio
    async def test_create_student_repository_error(self, student_service, mock_repository, sample_student_data):
        """Test error handling when repository fails."""
        mock_repository.get_by_criteria.return_value = []
        mock_repository.create.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await student_service.create_student(sample_student_data)
        
        assert "Failed to create student" in str(exc_info.value)


class TestStudentServiceRetrieval:
    """Tests for student retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_student_by_id_success(self, student_service, mock_repository, sample_student_in_db):
        """Test successful student retrieval by ID."""
        mock_repository.get_by_id.return_value = sample_student_in_db
        
        result = await student_service.get_student(sample_student_in_db.id)
        
        assert result.id == sample_student_in_db.id
        assert result.full_name == sample_student_in_db.full_name
        mock_repository.get_by_id.assert_called_once_with(sample_student_in_db.id)
    
    @pytest.mark.asyncio
    async def test_get_student_not_found(self, student_service, mock_repository):
        """Test retrieval when student doesn't exist."""
        mock_repository.get_by_id.return_value = None
        
        result = await student_service.get_student(uuid4())
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_students_success(self, student_service, mock_repository):
        """Test successful retrieval of all students."""
        students = [
            StudentInDB(
                id=uuid4(),
                full_name="John Doe",
                age=15,
                class_="10A",
                gender="Male",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            StudentInDB(
                id=uuid4(),
                full_name="Jane Doe",
                age=16,
                class_="11B",
                gender="Female",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]
        mock_repository.get_all.return_value = (students, 2)
        
        result_students, total = await student_service.get_all_students()
        
        assert len(result_students) == 2
        assert total == 2
        assert result_students[0].full_name == "John Doe"
        assert result_students[1].full_name == "Jane Doe"
    
    @pytest.mark.asyncio
    async def test_get_all_students_empty(self, student_service, mock_repository):
        """Test retrieval when no students exist."""
        mock_repository.get_all.return_value = ([], 0)
        
        result_students, total = await student_service.get_all_students()
        
        assert result_students == []
        assert total == 0
    
    @pytest.mark.asyncio
    async def test_get_all_students_with_pagination(self, student_service, mock_repository):
        """Test retrieval with pagination parameters."""
        students = [StudentInDB(
            id=uuid4(),
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )]
        mock_repository.get_all.return_value = (students, 100)
        
        result_students, total = await student_service.get_all_students(skip=10, limit=20)
        
        assert len(result_students) == 1
        assert total == 100
        mock_repository.get_all.assert_called_once_with(
            skip=10,
            limit=20,
            filters=None,
            sort_by=None,
            sort_order='asc'
        )
    
    @pytest.mark.asyncio
    async def test_get_all_students_with_filters(self, student_service, mock_repository):
        """Test retrieval with filter criteria."""
        students = [StudentInDB(
            id=uuid4(),
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )]
        mock_repository.get_all.return_value = (students, 1)
        
        filters = {'class_': '10A', 'gender': 'Male'}
        result_students, total = await student_service.get_all_students(filters=filters)
        
        assert len(result_students) == 1
        mock_repository.get_all.assert_called_once_with(
            skip=0,
            limit=100,
            filters=filters,
            sort_by=None,
            sort_order='asc'
        )
    
    @pytest.mark.asyncio
    async def test_get_all_students_with_sorting(self, student_service, mock_repository):
        """Test retrieval with sorting."""
        students = [StudentInDB(
            id=uuid4(),
            full_name="John Doe",
            age=15,
            class_="10A",
            gender="Male",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )]
        mock_repository.get_all.return_value = (students, 1)
        
        result_students, total = await student_service.get_all_students(
            sort_by='full_name',
            sort_order='desc'
        )
        
        assert len(result_students) == 1
        mock_repository.get_all.assert_called_once_with(
            skip=0,
            limit=100,
            filters=None,
            sort_by='full_name',
            sort_order='desc'
        )
    
    @pytest.mark.asyncio
    async def test_get_all_students_invalid_skip(self, student_service):
        """Test that negative skip raises error."""
        with pytest.raises(ValueError) as exc_info:
            await student_service.get_all_students(skip=-1)
        
        assert "skip must be non-negative" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_all_students_invalid_limit(self, student_service):
        """Test that invalid limit raises error."""
        with pytest.raises(ValueError) as exc_info:
            await student_service.get_all_students(limit=0)
        
        assert "limit must be at least 1" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_all_students_invalid_sort_order(self, student_service):
        """Test that invalid sort order raises error."""
        with pytest.raises(ValueError) as exc_info:
            await student_service.get_all_students(sort_order='invalid')
        
        assert "sort_order must be 'asc' or 'desc'" in str(exc_info.value)
