FROM python:3.11-slim

WORKDIR /app

# Shared libraries OpenCV and MediaPipe load at import time
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 libgl1 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py trainer.py ./
COPY templates templates
COPY static static

ENV PYTHONUNBUFFERED=1 PORT=5000
EXPOSE 5000

# One eventlet worker: per-connection state lives in this process's memory.
CMD gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
