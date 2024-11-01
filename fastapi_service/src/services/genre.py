from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from fastapi_service.src.core import config
from fastapi_service.src.core.logger import logger
from fastapi_service.src.db.elastic import (
    get_elastic,
    ElasticsearchRepository,
)
from fastapi_service.src.db.redis import get_redis, redis_cache
from fastapi_service.src.models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: ElasticsearchRepository):
        self.redis = redis
        self.elastic = elastic
        self.index = config.ELASTIC_GENRE_INDEX

    async def get_by_name(self, genre_name: str) -> Genre:
        es_query = {"query": {"match": {"name": genre_name}}}
        try:
            hits = await self.elastic.search(body=es_query)
            if len(genre_data := hits) > 0:
                return Genre(**genre_data[0]["_source"])
        except NotFoundError:
            logger.exception("'%s' genre wasn't found", genre_name)

    async def get_genres(self) -> list[Genre]:
        es_query = {"query": {"match_all": {}}}
        hits = await self.elastic.search(body=es_query)
        genres = [Genre(**hit["_source"]) for hit in hits]
        return genres

    @redis_cache("genre", Genre)
    async def get_by_id(self, genre_id: str) -> Genre:
        genre_data = await self.elastic.get(doc_id=genre_id)
        if genre_data:
            return Genre(**genre_data)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(
        redis, ElasticsearchRepository(elastic, config.ELASTIC_GENRE_INDEX)
    )
