"""
SignSpeak Backend - Main Application Entry Point
=================================================
This is the FastAPI application. Running this file starts the web server.

How it works:
1. FastAPI creates an HTTP/WebSocket server.
2. Requests come in from the browser (frontend).
3. FastAPI routes them to the correct handler function.
4. The handler processes the request (auth, database, AI inference) and returns a response.

The WebSocket endpoint is the most important one for sign language recognition:
  Browser → sends JPEG frame bytes → Backend runs MediaPipe + LSTM → sends back JSON result

To run the server:
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import get_db, create_tables, SessionLocal
from models.models import TranslationHistory
from routes import router

# Add Ai_model to Python path so we can import the inference module
AI_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Ai_model"))
sys.path.insert(0, AI_MODEL_PATH)

# ─── FastAPI App Setup ────────────────────────────────────────────────────────

app = FastAPI(
    title="SignSpeak API",
    description=(
        "AI-Based Sign Language Recognition System.\n\n"
        "Provides real-time ASL gesture recognition via WebSocket "
        "and REST endpoints for user management and translation history."
    ),
    version="1.0.0",
    docs_url="/api/docs",   # Swagger UI available at /api/docs
    redoc_url="/api/redoc",
)

# CORS (Cross-Origin Resource Sharing)
# This allows the frontend (running on port 5173) to call our backend (port 8000)
# Without this, browsers would block the requests for security reasons.

# Build allowed origins list dynamically
_allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative React port
    "http://127.0.0.1:5173",
]
# Add production frontend URL if set in environment
if settings.FRONTEND_URL:
    _allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all REST routes under /api prefix
app.include_router(router, prefix="/api")


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Runs when the server starts."""
    print("SignSpeak API starting up...")
    # Create database tables if they don't exist
    create_tables()
    print("Database tables ready.")

    # Pre-load the AI model in the background so the first WS connection is fast
    try:
        from inference import recognizer
        recognizer.load()
        print(f"AI model loaded successfully ({len(recognizer.labels)} signs).")
    except FileNotFoundError as e:
        print(f"WARNING: AI model not loaded - {e}")
        print("The /api/signs endpoint will use labels.json directly.")
        print("Train the model first: python Ai_model/train.py")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the server shuts down."""
    print("SignSpeak API shutting down...")


# ─── WebSocket: Real-Time Sign Recognition ────────────────────────────────────

@app.websocket("/ws/recognize")
async def websocket_recognize(
    websocket: WebSocket,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
):
    """
    WebSocket endpoint for real-time sign language recognition.

    Protocol:
      Client sends:  raw JPEG bytes of a video frame
      Server sends:  JSON string with recognition result

    Example server response:
      {
        "type": "recognition",
        "sign": "hello",
        "confidence": 0.92,
        "timestamp": "2025-01-01T12:00:00"
      }

    Or if no sign detected yet:
      {
        "type": "processing",
        "frames_buffered": 15,
        "frames_needed": 30
      }

    Why WebSocket instead of HTTP?
      HTTP is request-response: the client asks, the server answers.
      WebSocket keeps a persistent connection open, allowing the server to
      push results to the client as they are computed — essential for real-time streaming.
    """
    await websocket.accept()

    if not session_id:
        session_id = str(uuid.uuid4())

    db: Session = SessionLocal()

    try:
        from inference import recognizer

        # Reset the frame buffer for this new session
        recognizer.reset()

        await websocket.send_json({
            "type": "connected",
            "message": "SignSpeak recognition ready. Start signing!",
            "session_id": session_id,
        })

        last_sign = None  # Track last recognized sign to avoid duplicates

        while True:
            # Wait for the next frame (raw bytes) from the frontend
            frame_bytes = await websocket.receive_bytes()

            # Process the frame through MediaPipe + LSTM
            result = recognizer.process_frame(frame_bytes)

            if result is not None:
                sign_label, confidence = result

                # Only send result if it's a new sign (debounce)
                if sign_label != last_sign:
                    last_sign = sign_label

                    response = {
                        "type": "recognition",
                        "sign": sign_label,
                        "confidence": round(confidence, 4),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await websocket.send_json(response)

                    # Save to database if user is authenticated
                    if user_id:
                        try:
                            record = TranslationHistory(
                                user_id=user_id,
                                sign_label=sign_label,
                                confidence=confidence,
                                session_id=session_id,
                            )
                            db.add(record)
                            db.commit()
                        except Exception:
                            db.rollback()
            else:
                # Still accumulating frames - tell the client how many we have
                frames_buffered = len(recognizer.sequence_buffer)
                await websocket.send_json({
                    "type": "processing",
                    "frames_buffered": frames_buffered,
                    "frames_needed": 30,
                })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected (session: {session_id})")
    except FileNotFoundError as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Recognition error. Please refresh and try again.",
            })
        except Exception:
            pass
    finally:
        db.close()


# ─── Root Redirect ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to SignSpeak API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
