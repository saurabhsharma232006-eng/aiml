from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Registers a new student. Enforces unique email constraint and input validation.",
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new student record.
    Returns 400 Bad Request if a student with the same email already exists.
    """
    existing_student = crud.get_student_by_email(db, student_in.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email '{student_in.email}' already exists.",
        )
    return crud.create_student(db=db, student_in=student_in)


@router.get(
    "",
    response_model=schemas.PaginatedStudentResponse,
    status_code=status.HTTP_200_OK,
    summary="List students with filtering & pagination",
    description="Query students with optional course filter, search by name or course, and pagination.",
)
def list_students(
    course: Optional[str] = Query(
        default=None,
        description="Filter students by course name (case-insensitive substring)",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search students by name or course (case-insensitive substring)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return (1-100)",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of students matching the given filter criteria.
    """
    records, total = crud.get_students(
        db=db,
        course=course,
        search=search,
        offset=offset,
        limit=limit,
    )
    return schemas.PaginatedStudentResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=records,
    )


@router.get(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student by ID",
    description="Retrieve full details of a specific student using their unique integer ID.",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a student by ID. Returns 404 if the student does not exist.
    """
    student = crud.get_student_by_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return student


@router.put(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a student (PUT)",
    description="Updates existing student attributes. Supports partial or full updates.",
)
@router.patch(
    "/{student_id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a student (PATCH)",
    description="Updates existing student attributes. Supports partial or full updates.",
)
def update_student(
    student_id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates a student record.
    Returns 404 if student does not exist.
    Returns 400 if updating email to one that is already occupied by another student.
    """
    db_student = crud.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    # Check email uniqueness if email is being updated
    if student_update.email is not None and student_update.email.strip().lower() != db_student.email.lower():
        conflict_student = crud.get_student_by_email(db, student_update.email)
        if conflict_student and conflict_student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_update.email}' is already taken by another student (ID: {conflict_student.id}).",
            )

    return crud.update_student(db=db, db_student=db_student, student_update=student_update)


@router.delete(
    "/{student_id}",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a student",
    description="Deletes a student record permanently by ID.",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    """
    Deletes a student record. Returns 404 if the student does not exist.
    """
    db_student = crud.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    student_name = db_student.name
    crud.delete_student(db=db, db_student=db_student)
    return schemas.MessageResponse(
        message=f"Student '{student_name}' (ID: {student_id}) was successfully deleted.",
        details={"deleted_student_id": student_id, "student_name": student_name},
    )
