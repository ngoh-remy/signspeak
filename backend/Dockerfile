FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for potential OpenCV/MediaPipe usage
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Ai_model directory so the backend can import it
COPY Ai_model ./Ai_model

# Copy backend source code
COPY backend ./backend

WORKDIR /app/backend

# Expose port (Render/Railway sets $PORT dynamically)
EXPOSE 8000

# Start the server - Render/Railway provides $PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
