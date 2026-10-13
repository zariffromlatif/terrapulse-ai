# ProofPath AI - Cloud Run Production Dockerfile
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies if required for network/fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY proofpath/ ./proofpath/
COPY app.py .
COPY eval_benchmark.py .

# Create non-root user for Cloud Run security compliance
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Run FastAPI production server respecting Cloud Run's $PORT environment variable
CMD uvicorn proofpath.api:app --host 0.0.0.0 --port ${PORT:-8080}
