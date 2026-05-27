"""
SignSpeak Backend - Database Configuration
==========================================
Sets up the SQLAlchemy database engine and session factory.

Why SQLAlchemy?
  SQLAlchemy is an ORM (Object-Relational Mapper). Instead of writing raw SQL
  queries, we define Python classes that map to database tables. This makes the
  code more readable and reduces the risk of SQL injection attacks.

Why SQLite?
  SQLite is a file-based database — no separate server needed. Perfect for
  development and local demos. For production deployment, switch DATABASE_URL
  to a PostgreSQL or MySQL connection string.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create the database engine
# connect_args is required for SQLite to work with FastAPI's async handlers
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Session factory - each request gets its own database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    Automatically closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database (run once at startup)."""
    from models.models import User, TranslationHistory  # noqa: F401 - needed for table registration
    Base.metadata.create_all(bind=engine)
