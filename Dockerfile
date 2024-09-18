FROM python:3.10 AS base

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --verbose

# Application stage
FROM base AS app

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Updater stage
FROM base AS updater

RUN ln -fs /usr/share/zoneinfo/Europe/Prague /etc/localtime

WORKDIR /app

COPY scripts/ /app

CMD ["python", "script.py"]