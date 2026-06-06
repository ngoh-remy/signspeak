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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.responses import Response
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

# ─── CORS Middleware ──────────────────────────────────────────────────────────
# Custom CORS middleware that echoes the request origin back.
# This is more reliable than FastAPI's CORSMiddleware in some proxy setups
# and supports credentials correctly.

CORS_HEADERS = {
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With",
    "Access-Control-Max-Age": "600",
}


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    # Fallback to the production website if origin is stripped (common on mobile browsers)
    allowed_origin = origin if origin else "https://signspeak2.vercel.app"

    # Handle OPTIONS preflight — must return 200 with CORS headers immediately
    if request.method == "OPTIONS":
        headers = {**CORS_HEADERS, "Access-Control-Allow-Origin": allowed_origin}
        return Response(status_code=200, headers=headers)

    # For all other requests, process normally then add CORS headers
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value
    return response

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


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the server shuts down."""
    print("SignSpeak API shutting down...")




# ─── Root Redirect ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to SignSpeak API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
