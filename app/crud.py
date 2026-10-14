from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """Retrieve a single student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Retrieve a single student by their unique email address."""
    return db.query(Student).filter(Student.email == email.strip().lower()).first()


def get_students(
    db: Session,
    course: Optional[str] = None,
    search: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> Tuple[List[Student], int]:
    """
    Retrieve students with optional course filter, case-insensitive search by name,
    and pagination (offset and limit). Returns (records, total_matching_count).
    """
    query = db.query(Student)

    if course:
        query = query.filter(Student.course.ilike(f"%{course.strip()}%"))

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Student.name.ilike(search_pattern)) | (Student.course.ilike(search_pattern))
        )

    total_count = query.count()
    records = query.order_by(Student.id.asc()).offset(offset).limit(limit).all()

    return records, total_count


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create and persist a new student record in the database."""
    student_data = student_in.model_dump()
    # Normalize email to lower case
    student_data["email"] = student_data["email"].strip().lower()

    db_student = Student(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session,
    db_student: Student,
    student_update: StudentUpdate,
) -> Student:
    """
    Update fields of an existing student using provided partial/full payload.
    Only non-None fields are modified.
    """
    update_data = student_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "email" and value is not None:
            value = value.strip().lower()
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """Delete a student record from SQLite."""
    db.delete(db_student)
    db.commit()


def get_sanitized_students_context(db: Session, max_records: int = 60) -> Dict[str, Any]:
    """
    Fetches aggregate metrics and safe sanitized student records from SQLite
    to pass as grounded context to the Ollama LLM.
    Strictly avoids exposing direct SQL execution to user prompts.
    """
    total_students = db.query(func.count(Student.id)).scalar() or 0

    # Course breakdown
    course_counts = (
        db.query(Student.course, func.count(Student.id))
        .group_by(Student.course)
        .all()
    )
    course_summary = {
        (c if c else "Unassigned"): count for c, count in course_counts
    }

    # Fetch recent records (up to max_records)
    records = db.query(Student).order_by(Student.id.asc()).limit(max_records).all()

    students_roster = []
    for s in records:
        students_roster.append({
            "id": s.id,
            "name": s.name,
            "course": s.course or "Unassigned",
            "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
            "birth_year": s.date_of_birth.year if s.date_of_birth else None,
            "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None,
        })

    return {
        "total_enrolled_students": total_students,
        "course_distribution": course_summary,
        "sample_size": len(students_roster),
        "students": students_roster,
    }
