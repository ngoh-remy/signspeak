FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for potential OpenCV/MediaPipe usage
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Copy the Ai_model inference module so the backend can import it
COPY ../Ai_model /app/Ai_model

# Expose port (Render sets $PORT dynamically)
EXPOSE 8000

# Start the server - Render provides $PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
