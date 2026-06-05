FROM python:3.11-slim

# Force Python stdout/stderr to be unbuffered (immediate logging)
ENV PYTHONUNBUFFERED=1

# Create a non-root user (Hugging Face Spaces runs as user 1000)
RUN useradd -m -u 1000 user
WORKDIR /code

# Install system dependencies needed by MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the rest of the application files to the container
COPY --chown=user:user . /code

# Switch to the non-root user
USER user

# Hugging Face Spaces expects the container to listen on port 7860
EXPOSE 7860

# Start FastAPI via uvicorn on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
