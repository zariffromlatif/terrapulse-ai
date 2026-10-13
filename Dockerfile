# TerraPulse (CampTwin AI) - Google Cloud Run Production Dockerfile
# Track: Sustainability & Social Impact (Google Cloud AI Builder Cup 2026)
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered streaming stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install minimal curl for Cloud Run health checking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY terrapulse/ ./terrapulse/
COPY sample_data/ ./sample_data/
COPY app.py .
COPY eval_benchmark.py .

# Create non-root user for Google Cloud Run enterprise security compliance
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Run FastAPI production server respecting Cloud Run's dynamic $PORT variable
CMD ["sh", "-c", "uvicorn terrapulse.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
