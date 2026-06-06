FROM python:3.13-slim

WORKDIR /app
# Update package list, install g++, coreutils, and time, then clean package cache.
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    coreutils \
    time \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    confluent-kafka \
    sqlmodel \
    psycopg2-binary \
    python-dotenv \
    python-jose\
    pytest

COPY judge/ .
RUN rm -f src/models && mkdir -p src/models
COPY backend/src/models/ ./src/models/
CMD ["python", "main.py"]
