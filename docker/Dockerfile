FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY grilo_falante/ ./grilo_falante/
COPY visualizer_server/ ./visualizer_server/
COPY hub/ ./hub/
COPY app/ ./app/

RUN pip install --no-cache-dir -e ".[all]" && \
    pip install --no-cache-dir python-multipart

EXPOSE 8000

CMD ["uvicorn", "grilo_falante.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
