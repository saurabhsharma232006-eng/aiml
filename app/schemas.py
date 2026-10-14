from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class StudentBase(BaseModel):
    """Base schema containing common student fields."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the student",
        examples=["Sarah Connor"]
    )
    date_of_birth: date = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        examples=["2002-05-14"]
    )
    email: EmailStr = Field(
        ...,
        description="Unique student email address",
        examples=["sarah.connor@university.edu"]
    )
    phone: str = Field(
        ...,
        min_length=7,
        max_length=25,
        description="Contact phone number with area code",
        examples=["+1-555-019-2834"]
    )
    course: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name of the enrolled department or course",
        examples=["Computer Science"]
    )
    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Residential address of the student",
        examples=["404 Cyberdyne Way, Los Angeles, CA"]
    )
    enrollment_date: Optional[date] = Field(
        default_factory=date.today,
        description="Date student enrolled. Defaults to current date if omitted.",
        examples=["2024-09-01"]
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("date_of_birth must be a date in the past")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("name cannot be empty or whitespace only")
        return clean


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student record (partial or full)."""
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated full name"
    )
    date_of_birth: Optional[date] = Field(
        default=None,
        description="Updated date of birth in YYYY-MM-DD format"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Updated unique email address"
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=7,
        max_length=25,
        description="Updated contact phone number"
    )
    course: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated enrolled course"
    )
    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Updated residential address"
    )
    enrollment_date: Optional[date] = Field(
        default=None,
        description="Updated enrollment date"
    )

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value >= date.today():
            raise ValueError("date_of_birth must be a date in the past")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            clean = value.strip()
            if not clean:
                raise ValueError("name cannot be empty or whitespace only")
            return clean
        return value


class StudentResponse(StudentBase):
    """Schema returned to client upon query/mutation."""
    id: int = Field(..., description="Unique database identifier (Primary Key)")

    model_config = ConfigDict(from_attributes=True)


class PaginatedStudentResponse(BaseModel):
    """Paginated list envelope for students."""
    total: int = Field(..., description="Total count of records matching criteria")
    limit: int = Field(..., description="Maximum items per page")
    offset: int = Field(..., description="Number of items skipped")
    items: List[StudentResponse] = Field(..., description="List of student records")


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    details: Optional[Dict[str, Any]] = None


class AIQueryRequest(BaseModel):
    """Request payload for natural language query."""
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Natural language question about student records",
        examples=["How many students are enrolled in Computer Science?"]
    )
    model: Optional[str] = Field(
        default="llama3.2:1b",
        description="Ollama model identifier to execute query with",
        examples=["llama3.2:1b"]
    )


class AIQueryResponse(BaseModel):
    """Response returned from AI Assistant endpoint."""
    query: str = Field(..., description="The user's original natural language prompt")
    answer: str = Field(..., description="AI grounded explanation or fallback answer")
    grounded_data_summary: Dict[str, Any] = Field(
        ...,
        description="Sanitized statistical context extracted from SQLite"
    )
    model_used: str = Field(..., description="Model identifier used or targeted")
    ollama_available: bool = Field(..., description="True if local Ollama model answered; False if fallback was triggered")
