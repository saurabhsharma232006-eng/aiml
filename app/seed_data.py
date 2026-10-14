from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import Student

DUMMY_STUDENTS = [
    {
        "name": "Aarav Sharma",
        "date_of_birth": date(2003, 3, 15),
        "email": "aarav.sharma@example.edu",
        "phone": "+91-98765-43210",
        "course": "Computer Science",
        "address": "42 Tech Park Avenue, Bengaluru, Karnataka",
        "enrollment_date": date(2023, 8, 1),
    },
    {
        "name": "Elena Rostova",
        "date_of_birth": date(2004, 7, 22),
        "email": "elena.rostova@example.edu",
        "phone": "+1-555-014-9981",
        "course": "Data Science",
        "address": "128 Innovation Way, Austin, TX",
        "enrollment_date": date(2023, 8, 15),
    },
    {
        "name": "Marcus Vance",
        "date_of_birth": date(2006, 1, 10),
        "email": "marcus.vance@example.edu",
        "phone": "+1-555-018-3321",
        "course": "Cybersecurity",
        "address": "77 Beacon Street, Boston, MA",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "name": "Priya Patel",
        "date_of_birth": date(2006, 5, 18),
        "email": "priya.patel@example.edu",
        "phone": "+91-98234-56789",
        "course": "Computer Science",
        "address": "15 Green Valley Road, Ahmedabad, Gujarat",
        "enrollment_date": date(2024, 9, 5),
    },
    {
        "name": "Liam O'Connor",
        "date_of_birth": date(2002, 11, 4),
        "email": "liam.oconnor@example.edu",
        "phone": "+353-87-123-4567",
        "course": "Mechanical Engineering",
        "address": "8 College Green, Dublin, Ireland",
        "enrollment_date": date(2022, 9, 1),
    },
    {
        "name": "Sophia Chen",
        "date_of_birth": date(2006, 9, 30),
        "email": "sophia.chen@example.edu",
        "phone": "+1-555-012-7744",
        "course": "Artificial Intelligence",
        "address": "250 University Ave, Palo Alto, CA",
        "enrollment_date": date(2024, 9, 10),
    },
    {
        "name": "Tariq Mansoor",
        "date_of_birth": date(2003, 8, 19),
        "email": "tariq.mansoor@example.edu",
        "phone": "+971-50-987-6543",
        "course": "Electrical Engineering",
        "address": "Villa 14, Al Safa, Dubai, UAE",
        "enrollment_date": date(2023, 1, 15),
    },
    {
        "name": "Zoe Kim",
        "date_of_birth": date(2005, 12, 12),
        "email": "zoe.kim@example.edu",
        "phone": "+82-10-5555-8888",
        "course": "Data Science",
        "address": "88 Teheran-ro, Gangnam-gu, Seoul",
        "enrollment_date": date(2024, 2, 20),
    },
    {
        "name": "Mateo Alvarez",
        "date_of_birth": date(2006, 4, 2),
        "email": "mateo.alvarez@example.edu",
        "phone": "+34-612-345-678",
        "course": "Computer Science",
        "address": "Calle Mayor 33, Madrid, Spain",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "name": "Chloe Dupont",
        "date_of_birth": date(2004, 2, 14),
        "email": "chloe.dupont@example.edu",
        "phone": "+33-6-12-34-56-78",
        "course": "Cybersecurity",
        "address": "12 Rue de Rivoli, Paris, France",
        "enrollment_date": date(2023, 9, 1),
    },
]


def seed_database(db: Session = None) -> int:
    """
    Populates SQLite database with realistic student records.
    Idempotent: skips records whose email already exists in the database.
    """
    init_db()
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        inserted_count = 0
        for student_data in DUMMY_STUDENTS:
            existing = (
                db.query(Student)
                .filter(Student.email == student_data["email"].lower())
                .first()
            )
            if not existing:
                student = Student(**student_data)
                db.add(student)
                inserted_count += 1

        db.commit()
        return inserted_count
    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    print("Initializing SQLite tables and seeding initial dummy student records...")
    count = seed_database()
    print(f"Successfully seeded {count} new student record(s). (Total realistic records in pool: {len(DUMMY_STUDENTS)})")
