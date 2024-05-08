FROM python:3.10 AS app

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --verbose

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "6"]

FROM python:3.10 AS updater

# Set the working directory in the container
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --verbose

# Copy the dependencies file to the working directory
COPY scripts/ /app

# Set the default command to run your script
CMD ["python", "script.py"]