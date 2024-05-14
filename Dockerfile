FROM python:3.10 AS app

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --verbose

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

FROM python:3.10 AS updater

# set the time for Prague
RUN ln -fs /usr/share/zoneinfo/Europe/Prague /etc/localtime

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