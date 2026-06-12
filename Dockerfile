# Use official lightweight Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=src

# Set working directory
WORKDIR /app

# Install system compiler tools for packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dataset, backend source code, and compiled React frontend files
COPY data/ ./data
COPY src/ ./src
COPY static/ ./static

# Expose default port (Railway automatically overrides this)
EXPOSE 8000

# Start uvicorn server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
