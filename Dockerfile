FROM python:3.10-slim-bullseye AS base

RUN apt-get update && \
	apt-get -y -q --no-install-recommends install libgomp1

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /app/src
RUN mkdir -p /app/docker_valume
WORKDIR /app
COPY ./src ./src

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

