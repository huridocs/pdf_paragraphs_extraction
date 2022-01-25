FROM python:3.9.10-bullseye AS base

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir /app
RUN mkdir /app/src
WORKDIR /app
COPY ./src ./src

FROM base AS api
COPY docker-compose.yml .
CMD gunicorn -k uvicorn.workers.UvicornWorker --chdir ./src app:app --bind 0.0.0.0:5051

FROM base AS extract_pdf_paragraphs
COPY docker-compose.yml .
CMD python3 src/QueueProcessor.py

