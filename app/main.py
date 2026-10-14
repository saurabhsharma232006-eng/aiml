from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.routers import students, ai_query


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that runs startup and shutdown logic.
    Ensures SQLite tables are created prior to handling requests.
    """
    # Startup: Initialize database schema
    init_db()
    yield
    # Shutdown logic (if any cleanup is needed)


app = FastAPI(
    title="Students Database API",
    version="1.0.0",
    description=(
        "Production-ready FastAPI backend for Student Information Management.\n\n"
        "Features:\n"
        "- Full CRUD on Students with Pydantic v2 validation and persistent SQLite storage.\n"
        "- Filtering by course, name substring search, and offset/limit pagination.\n"
        "- Grounded Ollama AI natural language query endpoint with graceful fallback.\n"
        "- Comprehensive HTTP status codes and error responses."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Cross-Origin Resource Sharing (CORS) Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production environments as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(students.router)
app.include_router(ai_query.router)


@app.get(
    "/",
    tags=["Root"],
    summary="API Root Information",
    description="Returns welcome message, API metadata, and useful links.",
)
def root():
    return {
        "message": "Welcome to the Students Database API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "students_crud": "/students",
            "ai_assistant": "/students/ask-ai",
            "health_check": "/health",
        },
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Service Health Check",
    description="Checks service status and validates active SQLite database connectivity.",
    status_code=status.HTTP_200_OK,
)
def health_check(db: Session = Depends(get_db)):
    try:
        # Run a quick lightweight SQL check
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "1.0.0",
    }
