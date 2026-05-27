"""
SignSpeak Backend - API Routes
================================
This file defines all the HTTP API endpoints for the application.

Route groups:
  /api/auth/...     - User registration and login
  /api/signs/...    - List of supported signs
  /api/history/...  - User's translation history
  /api/health       - Server health check
"""

from datetime import datetime
from typing import Optional, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, TranslationHistory
from schemas import (
    UserRegister, UserResponse, UserLogin, TokenResponse,
    TranslationHistoryItem, TranslationHistoryResponse,
    SignsResponse, SignInfo, FrameResponse
)
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


# ─── Health Check ────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
def health_check():
    """
    Simple health check endpoint.
    Returns server status and current time.
    Used by the frontend to verify the backend is running.
    """
    return {
        "status": "healthy",
        "service": "SignSpeak API",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ─── Authentication Routes ───────────────────────────────────────────────────

@router.post("/auth/register", response_model=TokenResponse, tags=["Authentication"])
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Steps:
    1. Check if email or username already exists.
    2. Hash the password (never store plain text).
    3. Create and save the user record.
    4. Return a JWT token so the user is immediately logged in.
    """
    # Check for duplicate email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Check for duplicate username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken."
        )

    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = create_access_token(data={"sub": str(new_user.id)})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Log in with email and password. Returns a JWT access token.

    The token must be included in subsequent requests as:
      Authorization: Bearer <token>
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )

    token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    """Return information about the currently authenticated user."""
    return UserResponse.model_validate(current_user)


# ─── Signs Dictionary ─────────────────────────────────────────────────────────

@router.get("/signs", response_model=SignsResponse, tags=["Signs"])
def get_signs(
    search: Optional[str] = Query(None, description="Filter signs by keyword"),
    limit: int = Query(100, le=2000),
    offset: int = Query(0, ge=0),
):
    """
    Return the list of all signs supported by the AI model.
    Supports search filtering and pagination.
    """
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Ai_model"))

    try:
        from inference import recognizer
        all_labels = recognizer.get_all_labels()
    except Exception:
        # If model isn't trained yet, return from labels.json directly
        import json
        labels_path = os.path.join(os.path.dirname(__file__), "..", "Ai_model", "labels.json")
        if os.path.exists(labels_path):
            with open(labels_path) as f:
                all_labels = json.load(f)
        else:
            all_labels = []

    # Filter by search term
    if search:
        all_labels = [l for l in all_labels if search.lower() in l.lower()]

    total = len(all_labels)
    paginated = all_labels[offset: offset + limit]

    return SignsResponse(
        signs=[SignInfo(label=l, index=i) for i, l in enumerate(paginated)],
        total=total
    )


# ─── Translation History ──────────────────────────────────────────────────────

@router.get("/history", response_model=TranslationHistoryResponse, tags=["History"])
def get_history(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's translation history, newest first."""
    query = (
        db.query(TranslationHistory)
        .filter(TranslationHistory.user_id == current_user.id)
        .order_by(TranslationHistory.created_at.desc())
    )
    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return TranslationHistoryResponse(
        items=[TranslationHistoryItem.model_validate(item) for item in items],
        total=total
    )


@router.delete("/history", tags=["History"])
def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all translation history for the current user."""
    db.query(TranslationHistory).filter(
        TranslationHistory.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "History cleared successfully."}


@router.post("/history/record", tags=["History"])
def record_translation(
    sign_label: str,
    confidence: float,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually record a recognized sign to history. Called by the WebSocket handler."""
    record = TranslationHistory(
        user_id=current_user.id,
        sign_label=sign_label,
        confidence=confidence,
        session_id=session_id,
    )
    db.add(record)
    db.commit()
    return {"recorded": True}
