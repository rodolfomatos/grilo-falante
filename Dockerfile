# Grilo Falante v3.0 - Dockerfile
# Multi-stage build for production

FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY grilo_admin/ ./grilo_admin/
COPY grilo_falante/ ./grilo_falante/
COPY docs/ ./docs/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV GRILO_ADMIN_JWT_SECRET=changeme-in-production
ENV GRILO_STORAGE_PATH=/app/data/ilhas.json

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["uvicorn", "grilo_admin:app", "--host", "0.0.0.0", "--port", "8001"]
