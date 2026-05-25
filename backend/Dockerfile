FROM python:3.13-slim

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./

RUN pip install uv

RUN uv sync --frozen

COPY backend/ ./

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]