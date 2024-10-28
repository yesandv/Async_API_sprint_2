FROM python:3.12

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY functional tests/functional
COPY settings.py conftest.py .env tests/
