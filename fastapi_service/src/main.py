from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from fastapi_service.src.api.v1 import films, persons, genres
from fastapi_service.src.core import config
from fastapi_service.src.db import redis, elastic


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{config.ELASTIC_SCHEME}://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"
        ]
    )
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    default_response_class=JSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router)
app.include_router(persons.router)
app.include_router(genres.router)
