FROM python:3.11-slim

WORKDIR /app

# Cài system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipenv files trước
COPY Pipfile Pipfile.lock ./

# Cài Pipenv và install tất cả dependencies từ Pipfile.lock
RUN pip install --no-cache-dir pipenv && \
    pipenv install --deploy --system

# Copy toàn bộ source code
COPY . .

EXPOSE 8000

# Chạy migration rồi start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]