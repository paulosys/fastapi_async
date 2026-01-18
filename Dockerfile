FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.2.1

COPY pyproject.toml poetry.lock* README.md ./

RUN poetry install --no-ansi --without dev --no-root

COPY . .

EXPOSE 8000

CMD ["uvicorn", "fastapi_async.app:app", "--host", "0.0.0.0", "--port", "8000"]
