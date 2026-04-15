FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY pyproject.toml README.md ./
COPY grilo_falante/ ./grilo_falante/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "grilo_falante.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
