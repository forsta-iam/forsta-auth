FROM python:3.7

WORKDIR /app

COPY . /app

RUN apt update && apt install gcc libxmlsec1-dev libpq-dev -y && pip install pipenv && pipenv install --system --deploy

ENTRYPOINT /app/docker-entrypoint.sh

EXPOSE 8000
