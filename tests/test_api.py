import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Student
from app.seed_data import seed_database

# Use an isolated in-memory or dedicated test SQLite database
TEST_DATABASE_URL = "sqlite:///./test_students.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override app dependency
app.dependency_overrides[get_db] = override_get_db

# Setup client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create fresh tables before each test and drop them afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_students.db"):
        try:
            os.remove("./test_students.db")
        except PermissionError:
            pass


def test_root_and_health():
    """Test root and health endpoints."""
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert "Students Database API" in r_root.json()["message"]

    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"
    assert r_health.json()["database"] == "healthy"


def test_create_student_success():
    """Test successful student creation with valid payload."""
    payload = {
        "name": "Alan Turing",
        "date_of_birth": "1912-06-23",
        "email": "alan.turing@cambridge.edu",
        "phone": "+44-20-7946-0912",
        "course": "Computer Science",
        "address": "Bletchley Park, Milton Keynes",
        "enrollment_date": "2024-01-15",
    }
    res = client.post("/students", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["name"] == "Alan Turing"
    assert data["email"] == "alan.turing@cambridge.edu"
    assert data["course"] == "Computer Science"


def test_create_student_duplicate_email():
    """Test that creating a student with an existing email returns 400 Bad Request."""
    payload = {
        "name": "Ada Lovelace",
        "date_of_birth": "1915-12-10",
        "email": "ada.lovelace@analytical.org",
        "phone": "+44-20-7946-0123",
        "course": "Mathematics",
    }
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    # Attempt duplicate registration
    res2 = client.post("/students", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_create_student_validation_errors():
    """Test validation errors for future DOB and malformed email."""
    # Future DOB
    res_dob = client.post("/students", json={
        "name": "Marty McFly",
        "date_of_birth": "2099-01-01",
        "email": "marty@hillvalley.com",
        "phone": "+1-555-888-9999",
    })
    assert res_dob.status_code == 422

    # Malformed email
    res_email = client.post("/students", json={
        "name": "Doc Brown",
        "date_of_birth": "1950-01-01",
        "email": "not-an-email",
        "phone": "+1-555-888-9999",
    })
    assert res_email.status_code == 422


def test_get_student_by_id():
    """Test retrieving student by ID and 404 for missing ID."""
    # Create student
    payload = {
        "name": "Grace Hopper",
        "date_of_birth": "1906-12-09",
        "email": "grace.hopper@navy.mil",
        "phone": "+1-555-908-1122",
        "course": "Computer Systems",
    }
    create_res = client.post("/students", json=payload)
    student_id = create_res.json()["id"]

    # Existing ID
    get_res = client.get(f"/students/{student_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Grace Hopper"

    # Non-existing ID
    missing_res = client.get("/students/99999")
    assert missing_res.status_code == 404
    assert "not found" in missing_res.json()["detail"].lower()


def test_update_student():
    """Test updating existing student, 404 check, and email collision check."""
    # Create student 1
    s1 = client.post("/students", json={
        "name": "Claude Shannon",
        "date_of_birth": "1916-04-30",
        "email": "shannon@mit.edu",
        "phone": "+1-555-123-4567",
        "course": "Information Theory",
    }).json()

    # Create student 2
    s2 = client.post("/students", json={
        "name": "John von Neumann",
        "date_of_birth": "1903-12-28",
        "email": "vonneumann@ias.edu",
        "phone": "+1-555-987-6543",
        "course": "Applied Mathematics",
    }).json()

    # Successful update via PUT
    update_res = client.put(f"/students/{s1['id']}", json={
        "course": "Advanced Information Theory",
        "phone": "+1-555-000-1111",
    })
    assert update_res.status_code == 200
    assert update_res.json()["course"] == "Advanced Information Theory"
    assert update_res.json()["phone"] == "+1-555-000-1111"

    # Successful update via PATCH
    patch_res = client.patch(f"/students/{s1['id']}", json={
        "address": "Cambridge, MA"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["address"] == "Cambridge, MA"
    assert patch_res.json()["course"] == "Advanced Information Theory"

    # Attempt to change s1 email to s2 email (should conflict -> 400)
    conflict_res = client.put(f"/students/{s1['id']}", json={"email": "vonneumann@ias.edu"})
    assert conflict_res.status_code == 400
    assert "already taken" in conflict_res.json()["detail"]

    # 404 on missing ID
    missing_update = client.put("/students/8888", json={"name": "Nobody"})
    assert missing_update.status_code == 404


def test_delete_student():
    """Test deleting student and 404 behavior."""
    s = client.post("/students", json={
        "name": "Linus Torvalds",
        "date_of_birth": "1969-12-28",
        "email": "linus@kernel.org",
        "phone": "+1-555-321-4321",
        "course": "Operating Systems",
    }).json()

    # Delete
    del_res = client.delete(f"/students/{s['id']}")
    assert del_res.status_code == 200
    assert "successfully deleted" in del_res.json()["message"]

    # Verify gone
    get_res = client.get(f"/students/{s['id']}")
    assert get_res.status_code == 404

    # Second delete returns 404
    del_res_again = client.delete(f"/students/{s['id']}")
    assert del_res_again.status_code == 404


def test_filtering_and_pagination():
    """Test filtering by course, search by name, and pagination limit/offset."""
    # Seed 3 distinct students
    client.post("/students", json={
        "name": "Alice Smith",
        "date_of_birth": "2002-01-01",
        "email": "alice@school.edu",
        "phone": "+1-555-111-2222",
        "course": "Robotics",
    })
    client.post("/students", json={
        "name": "Bob Jones",
        "date_of_birth": "2003-02-02",
        "email": "bob@school.edu",
        "phone": "+1-555-222-3333",
        "course": "Robotics",
    })
    client.post("/students", json={
        "name": "Charlie Brown",
        "date_of_birth": "2004-03-03",
        "email": "charlie@school.edu",
        "phone": "+1-555-333-4444",
        "course": "Cybersecurity",
    })

    # Filter by course "Robotics"
    r_filter = client.get("/students?course=Robotics")
    assert r_filter.status_code == 200
    data_filter = r_filter.json()
    assert data_filter["total"] == 2
    assert len(data_filter["items"]) == 2

    # Search by name "Charlie"
    r_search = client.get("/students?search=Charlie")
    assert r_search.status_code == 200
    assert r_search.json()["total"] == 1
    assert r_search.json()["items"][0]["name"] == "Charlie Brown"

    # Pagination: limit=1, offset=1
    r_page = client.get("/students?limit=1&offset=1")
    assert r_page.status_code == 200
    data_page = r_page.json()
    assert data_page["total"] == 3
    assert len(data_page["items"]) == 1
    assert data_page["limit"] == 1
    assert data_page["offset"] == 1


def test_ask_ai_endpoint_fallback():
    """
    Test the /students/ask-ai endpoint.
    When Ollama is offline, it should gracefully fall back to SQLite grounded facts.
    """
    # Insert a student born after 2005
    client.post("/students", json={
        "name": "Young Prodigy",
        "date_of_birth": "2007-06-15",
        "email": "prodigy@school.edu",
        "phone": "+1-555-999-0000",
        "course": "Quantum Computing",
    })

    payload = {
        "query": "How many students are enrolled?",
        "model": "llama3.2:1b"
    }
    res = client.post("/students/ask-ai", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert "grounded_data_summary" in data
    assert data["grounded_data_summary"]["total_enrolled_students"] >= 1
    assert "answer" in data
    assert len(data["answer"]) > 0


def test_seed_database_execution():
    """Verify seed_database populates records cleanly."""
    db = TestingSessionLocal()
    try:
        count = seed_database(db=db)
        assert count > 0
        total = db.query(Student).count()
        assert total >= 8

        # Running again is idempotent (skips existing)
        re_count = seed_database(db=db)
        assert re_count == 0
    finally:
        db.close()
