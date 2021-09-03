FROM python:3.9-bullseye

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN adduser appuser
USER appuser
WORKDIR /home/appuser
COPY --chown=appuser . .

ENV FLASK_APP app.py

CMD gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:5050

