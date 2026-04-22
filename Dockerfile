# Dockerfile - Tối ưu cho FastAPI + Pipenv + PostgreSQL
FROM python:3.11-slim

WORKDIR /app

# Cài system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipenv files
COPY Pipfile Pipfile.lock ./

# Cài Pipenv và dependencies
RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --system --ignore-pipfile

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Chạy migration rồi start app
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]