# 🎓 Students Database CRUD & AI Assistant API

A production-ready, modular **FastAPI** backend featuring persistent **SQLite** storage via **SQLAlchemy**, strict **Pydantic v2** data validation, comprehensive HTTP error handling, dummy seed data, and a secure **Ollama-based natural language QA endpoint** with grounded context.

---

## 📌 Project Overview

This service provides a centralized Student Information System API designed to handle student enrollment, profile records, and queries. Built according to clean architecture principles, it guarantees data integrity, query isolation, and safe LLM grounding (avoiding raw SQL execution vulnerabilities).

### Key Features:
- **FastAPI Framework**: High-performance asynchronous REST API with auto-generated OpenAPI / Swagger documentation.
- **Relational SQLite Storage**: Thread-safe persistent database layer using SQLAlchemy ORM.
- **Pydantic v2 Validation**: Comprehensive schema validation for email format, phone numbers, past date-of-birth constraints, and input sanitization.
- **Full CRUD Capabilities**: Create, read (with filters, substring search, and limit/offset pagination), update, and delete.
- **Grounded AI Assistant (Ollama)**: Natural language question-answering powered by local LLMs (e.g., `llama3.2:1b`).
- **Resilient Fallback Mode**: If the local Ollama daemon is offline, the AI endpoint automatically generates a grounded statistical summary directly from the SQLite database.
- **Ready-to-use Seed Data**: Pre-loaded with 10 realistic, diverse international student records.

---

## 🏗️ Project Architecture

```
EWB/
├── app/
│   ├── __init__.py              # Package marker & version info
│   ├── main.py                  # FastAPI app initialization, CORS, routers, lifespan
│   ├── database.py              # SQLite engine, SessionLocal, get_db dependency
│   ├── models.py                # SQLAlchemy Student ORM model
│   ├── schemas.py               # Pydantic v2 request/response models & validators
│   ├── crud.py                  # Database queries, filters, mutations, context extractor
│   ├── seed_data.py             # Script to populate realistic dummy student records
│   └── routers/
│       ├── __init__.py
│       ├── students.py          # CRUD endpoints (/students)
│       └── ai_query.py          # Grounded Ollama QA endpoint (/students/ask-ai)
├── tests/
│   ├── __init__.py
│   └── test_api.py              # Pytest integration & unit test suite (100% pass)
├── .gitignore                   # Ignore rules for .venv, SQLite DBs, bytecode, IDEs
├── requirements.txt             # Pinned production and test dependencies
└── README.md                    # Comprehensive documentation and API guide
```

---

## 🛠️ Tech Stack & Dependencies

| Component | Library / Tool | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core runtime |
| **API Framework** | FastAPI & Starlette | Routing, DI, request handling |
| **ASGI Server** | Uvicorn (standard) | High-performance async server |
| **ORM / DB** | SQLAlchemy 2.0+ & SQLite | Data persistence & transaction management |
| **Data Validation** | Pydantic v2 & Email-Validator | Schema enforcement and type safety |
| **HTTP Client** | HTTPX | Asynchronous communication with Ollama |
| **LLM Runtime** | Ollama (`llama3.2:1b`) | Optional local natural language QA |
| **Testing** | Pytest | Automated test coverage |

---

## 📋 Data Schema: Student Model

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Auto (PK) | Unique auto-incrementing student ID |
| `name` | String(100) | Yes | Full student name (min 1 char, non-empty) |
| `date_of_birth` | Date | Yes | Birth date (`YYYY-MM-DD`). Must be in the past |
| `email` | EmailStr | Yes (Unique) | Valid, unique email address |
| `phone` | String(25) | Yes | Valid contact phone number with area code |
| `course` | String(100) | Optional | Course or department enrolled |
| `address` | String(255) | Optional | Residential address |
| `enrollment_date` | Date | Optional | Date enrolled (defaults to current date) |

---

## 🚀 Quickstart & Setup Guide

### 1. Clone or Open the Repository
```bash
cd "c:\Users\Admin\Downloads\CERTIFICATE WORK\EWB"
```

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the Database with Realistic Records
Populate the SQLite database (`students.db`) with 10 dummy students:
```bash
python -m app.seed_data
```
*(Note: This script is idempotent. Running it again will safely skip existing records without causing duplicate errors).*

### 5. Launch the FastAPI Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The application will start at: **`http://127.0.0.1:8000`**

---

## 📖 Interactive API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 🧪 Running Automated Tests

Run the full automated test suite verifying CRUD operations, edge cases, duplicate constraints, and the AI fallback:
```bash
pytest -v
```

---

## 📡 API Reference & cURL Testing Examples

### 1. Health Check
- **Endpoint**: `GET /health`
```bash
curl -X GET "http://127.0.0.1:8000/health"
```
**Sample 200 Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "version": "1.0.0"
}
```

---

### 2. Create a Student
- **Endpoint**: `POST /students`
- **Status Codes**: `201 Created`, `400 Bad Request` (duplicate email), `422 Unprocessable Entity` (validation error)

```bash
curl -X POST "http://127.0.0.1:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alex Mercer",
    "date_of_birth": "2003-11-20",
    "email": "alex.mercer@university.edu",
    "phone": "+1-555-019-8877",
    "course": "Robotics Engineering",
    "address": "500 Manhattan Blvd, New York, NY",
    "enrollment_date": "2024-09-01"
  }'
```
**Sample 201 Response:**
```json
{
  "id": 11,
  "name": "Alex Mercer",
  "date_of_birth": "2003-11-20",
  "email": "alex.mercer@university.edu",
  "phone": "+1-555-019-8877",
  "course": "Robotics Engineering",
  "address": "500 Manhattan Blvd, New York, NY",
  "enrollment_date": "2024-09-01"
}
```

---

### 3. List Students (Filtering & Pagination)
- **Endpoint**: `GET /students`
- **Query Parameters**:
  - `course` (optional): Filter by course name substring
  - `search` (optional): Case-insensitive search on student name or course
  - `offset` (default: 0): Skip N items
  - `limit` (default: 20, max: 100): Page size

#### A. List with Pagination:
```bash
curl -X GET "http://127.0.0.1:8000/students?limit=5&offset=0"
```

#### B. Filter by Course:
```bash
curl -X GET "http://127.0.0.1:8000/students?course=Computer%20Science"
```

#### C. Search by Name:
```bash
curl -X GET "http://127.0.0.1:8000/students?search=Aarav"
```
**Sample 200 Response:**
```json
{
  "total": 1,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "name": "Aarav Sharma",
      "date_of_birth": "2003-03-15",
      "email": "aarav.sharma@example.edu",
      "phone": "+91-98765-43210",
      "course": "Computer Science",
      "address": "42 Tech Park Avenue, Bengaluru, Karnataka",
      "enrollment_date": "2023-08-01"
    }
  ]
}
```

---

### 4. Get Student by ID
- **Endpoint**: `GET /students/{student_id}`
- **Status Codes**: `200 OK`, `404 Not Found`

```bash
curl -X GET "http://127.0.0.1:8000/students/1"
```

---

### 5. Update Student Record (PUT or PATCH)
- **Endpoint**: `PUT /students/{student_id}` or `PATCH /students/{student_id}`
- **Status Codes**: `200 OK`, `400 Bad Request` (email conflict), `404 Not Found`

```bash
curl -X PATCH "http://127.0.0.1:8000/students/1" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "Advanced Artificial Intelligence",
    "phone": "+91-98765-00000"
  }'
```

---

### 6. Delete Student Record
- **Endpoint**: `DELETE /students/{student_id}`
- **Status Codes**: `200 OK`, `404 Not Found`

```bash
curl -X DELETE "http://127.0.0.1:8000/students/1"
```
**Sample 200 Response:**
```json
{
  "message": "Student 'Aarav Sharma' (ID: 1) was successfully deleted.",
  "details": {
    "deleted_student_id": 1,
    "student_name": "Aarav Sharma"
  }
}
```

---

## 🤖 Ollama Natural Language QA Endpoint (`/students/ask-ai`)

### Safe Grounding Architecture
> [!IMPORTANT]
> To prevent SQL injection and hallucinations, **the application never allows direct unrestricted SQL generation**.
> Instead:
> 1. SQLite extracts a sanitized, read-only snapshot containing aggregate metrics (total counts, course distributions) and safe student roster summaries.
> 2. The sanitized JSON is injected into a tightly constrained system prompt.
> 3. Ollama generates a factual, grounded response based **solely** on the verified SQLite snapshot.

### Testing the AI Feature Locally

#### Step 1: Install & Start Ollama
1. Download Ollama from [https://ollama.com](https://ollama.com).
2. Start the daemon (usually runs automatically at `http://localhost:11434`):
   ```bash
   ollama serve
   ```
3. Pull the recommended lightweight model:
   ```bash
   ollama pull llama3.2:1b
   ```

#### Step 2: Send Natural Language Queries
```bash
curl -X POST "http://127.0.0.1:8000/students/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many students are enrolled?",
    "model": "llama3.2:1b"
  }'
```

```bash
curl -X POST "http://127.0.0.1:8000/students/ask-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "List all students born after 2005.",
    "model": "llama3.2:1b"
  }'
```

#### Step 3: Graceful Offline Fallback Mode
If Ollama is not installed or currently stopped, the endpoint **will not crash**. It returns a clean HTTP 200 response with `ollama_available: false` and computes verified facts directly from SQLite:
```json
{
  "query": "List all students born after 2005.",
  "answer": "ℹ️ [Offline Mode]: Ollama daemon is currently unreachable. Returning verified SQLite database facts directly:\n• Students born after 2005 (4 found):\n  - Marcus Vance (ID: 3, Course: Cybersecurity, Born: 2006-01-10)\n  - Priya Patel (ID: 4, Course: Computer Science, Born: 2006-05-18)\n  - Sophia Chen (ID: 6, Course: Artificial Intelligence, Born: 2006-09-30)\n  - Mateo Alvarez (ID: 9, Course: Computer Science, Born: 2006-04-02)\n\nTip: Start Ollama with `ollama run llama3.2:1b` to enable full natural language responses.",
  "grounded_data_summary": {
    "total_enrolled_students": 10,
    "course_distribution": {
      "Artificial Intelligence": 1,
      "Computer Science": 3,
      "Cybersecurity": 2,
      "Data Science": 2,
      "Electrical Engineering": 1,
      "Mechanical Engineering": 1
    },
    "sample_size": 10
  },
  "model_used": "llama3.2:1b",
  "ollama_available": false
}
```

---

## 🛡️ Error Handling Specifications

| Status Code | Reason | Example Condition |
|---|---|---|
| `200 OK` | Successful retrieval, update, or deletion | Querying an existing student ID |
| `201 Created` | Successful resource creation | Student registered successfully |
| `400 Bad Request` | Uniqueness conflict | Registering with an existing email address |
| `404 Not Found` | Resource not found | Requesting student ID `99999` |
| `422 Unprocessable` | Input validation failure | `date_of_birth` in future or malformed email |
| `500 Internal` | Unexpected server condition | Database connection breakdown |

---

## 📄 License
This project is open-source and free to use under the MIT License.
