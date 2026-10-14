import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Configurable SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

# For SQLite, check_same_thread=False allows multiple threads to interact with the connection
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True for debugging SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and ensures it is properly closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes database tables defined in SQLAlchemy models.
    """
    # Import models here to ensure they are registered with Base metadata
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
