FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY fastapi_service/src ./fastapi_service/src
COPY .env .
