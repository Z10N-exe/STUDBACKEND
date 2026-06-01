from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StudentBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=4, le=25)
    class_: str = Field(..., min_length=1, max_length=20)
    gender: str = Field(...)
    
    @validator('gender')
    def validate_gender(cls, v):
        allowed_genders = ['Male', 'Female', 'Other']
        if v not in allowed_genders:
            raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
        return v
    
    @validator('class_')
    def validate_class(cls, v):
        if not v.strip():
            raise ValueError('Class cannot be empty')
        return v.strip()
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=4, le=25)
    class_: Optional[str] = Field(None, min_length=1, max_length=20)
    gender: Optional[str] = Field(None)
    
    @validator('gender')
    def validate_gender(cls, v):
        if v is not None:
            allowed_genders = ['Male', 'Female', 'Other']
            if v not in allowed_genders:
                raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
        return v
    
    @validator('class_')
    def validate_class(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Class cannot be empty')
        return v.strip() if v else v
    
    class Config:
        from_attributes = True
        populate_by_name = True


class StudentInDB(StudentBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(None)
    
    class Config:
        from_attributes = True


class StudentResponse(StudentInDB):
    pass


class StudentListResponse(BaseModel):
    students: List[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentDB(Base):
    __tablename__ = 'students'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    class_ = Column('class', String(20), nullable=False)
    gender = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        CheckConstraint('age >= 4 AND age <= 25', name='check_age_range'),
        CheckConstraint("gender IN ('Male', 'Female', 'Other')", name='check_gender_values'),
        UniqueConstraint('full_name', 'class', name='unique_student_constraint'),
    )
    
    def to_pydantic(self) -> StudentInDB:
        return StudentInDB(
            id=self.id,
            full_name=self.full_name,
            age=self.age,
            class_=self.class_,
            gender=self.gender,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
        )
    
    @classmethod
    def from_pydantic(cls, student: StudentCreate) -> 'StudentDB':
        return cls(
            full_name=student.full_name,
            age=student.age,
            class_=student.class_,
            gender=student.gender,
        )