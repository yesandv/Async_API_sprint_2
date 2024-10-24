import os
from logging import config as logging_config

from dotenv import load_dotenv

from fastapi_service.src.core.logger import LOGGING

load_dotenv()

logging_config.dictConfig(LOGGING)

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

ELASTIC_SCHEME = os.getenv("ELASTIC_SCHEME", "http")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
ELASTIC_FILM_INDEX = os.getenv("ES_FILM_INDEX", "movies")
ELASTIC_GENRE_INDEX = os.getenv("ES_GENRE_INDEX", "genres")
ELASTIC_PERSON_INDEX = os.getenv("ES_PERSON_INDEX", "persons")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
