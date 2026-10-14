from datetime import date
from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class Student(Base):
    """
    SQLAlchemy model representing a Student entity in SQLite.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(25), nullable=False)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=False, default=date.today)

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.name}', email='{self.email}', course='{self.course}')>"

    def to_dict(self) -> dict:
        """Helper method to convert student model into a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "email": self.email,
            "phone": self.phone,
            "course": self.course,
            "address": self.address,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
        }
