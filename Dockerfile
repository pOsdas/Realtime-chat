FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl git build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*


RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pipx && \
    pipx install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=chat_project.settings

EXPOSE 8005

CMD ["poetry", "run", "daphne", "-b", "0.0.0.0", "-p", "8005", "chat_project.asgi:application"]
