FROM python:3.13-slim

WORKDIR /app
# Update package list, install g++, coreutils, and time, then clean package cache.
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    coreutils \
    time \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "fastapi[standard]" \
    sqlmodel \
    psycopg2-binary \
    python-dotenv \
    python-jose

COPY judge/ .
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]