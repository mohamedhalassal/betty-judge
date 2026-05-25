FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --frozen

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0"]