FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Ai_model directory so the backend can import it
COPY Ai_model ./Ai_model

# Copy backend source code
COPY backend ./backend

WORKDIR /app/backend

# Expose default port
EXPOSE 8000

# Use shell form so $PORT environment variable is properly expanded
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
