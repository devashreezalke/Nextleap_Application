# Use official full Python base image (contains compilers and development headers)
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=src

# Set working directory
WORKDIR /app

# Upgrade pip to ensure latest wheel support
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dataset, backend source code, and compiled React frontend files
COPY data/ ./data
COPY src/ ./src
COPY static/ ./static

# Expose default port
EXPOSE 8000

# Start uvicorn server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
