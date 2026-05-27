"""
SignSpeak Backend - Database Models
=====================================
SQLAlchemy ORM models define the database tables.

Tables:
  - users: Stores registered user accounts
  - translation_history: Stores every recognized sign per user session
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    Represents a registered user of the SignSpeak application.

    Fields:
      id          - Auto-incrementing primary key
      username    - Unique display name
      email       - Unique email address (used for login)
      hashed_pw   - bcrypt-hashed password (we never store plain-text passwords)
      is_active   - Whether the account is enabled
      created_at  - When the account was created
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: one user has many translation history records
    translations = relationship("TranslationHistory", back_populates="user",
                                cascade="all, delete-orphan")


class TranslationHistory(Base):
    """
    Records every sign recognized for a user.

    Fields:
      id          - Auto-incrementing primary key
      user_id     - Foreign key to the User who made the translation
      sign_label  - The recognized sign word (e.g., "hello")
      confidence  - Model confidence (0.0 to 1.0)
      session_id  - Groups translations within the same camera session
      created_at  - Timestamp of recognition
    """
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sign_label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    session_id = Column(String(36), nullable=True)  # UUID string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to User
    user = relationship("User", back_populates="translations")
