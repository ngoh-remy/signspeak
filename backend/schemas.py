"""
SignSpeak Backend - Pydantic Schemas
======================================
Pydantic schemas define the shape of data coming IN (request bodies)
and going OUT (responses) from our API.

Why Pydantic?
  Pydantic validates data automatically. If a request is missing a required field
  or has the wrong type, FastAPI returns a 422 error with a clear explanation.
  This protects our API from malformed requests.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    """Data required to register a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Data required to log in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Data returned about a user (never includes password)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Returned after successful login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Recognition Schemas ──────────────────────────────────────────────────────

class RecognitionResult(BaseModel):
    """A single sign recognition result."""
    sign: str
    confidence: float
    timestamp: datetime


class FrameResponse(BaseModel):
    """Response from the single-frame HTTP recognition endpoint."""
    recognized: bool
    sign: Optional[str] = None
    confidence: Optional[float] = None
    message: str = ""


# ─── Translation History Schemas ─────────────────────────────────────────────

class TranslationHistoryItem(BaseModel):
    """A single item in translation history."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    sign_label: str
    confidence: float
    session_id: Optional[str] = None
    created_at: datetime


class TranslationHistoryResponse(BaseModel):
    """Paginated list of translation history."""
    items: List[TranslationHistoryItem]
    total: int


# ─── Signs Dictionary Schema ──────────────────────────────────────────────────

class SignInfo(BaseModel):
    """Information about a supported sign."""
    label: str
    index: int


class SignsResponse(BaseModel):
    """List of all supported signs."""
    signs: List[SignInfo]
    total: int
