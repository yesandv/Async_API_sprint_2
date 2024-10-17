from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from src.core import config
from src.core.logger import logger
from src.db.elastic import get_elastic
from src.db.redis import get_redis, redis_cache
from src.models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = config.ELASTIC_GENRE_INDEX

    async def get_by_name(self, genre_name: str) -> Genre:
        es_query = {"query": {"match": {"name": genre_name}}}
        response = await self.elastic.search(index=self.index, body=es_query)
        try:
            if len(genre_data := response["hits"]["hits"]) > 0:
                return Genre(**genre_data[0]["_source"])
        except NotFoundError:
            logger.exception("'%s' genre wasn't found", genre_name)

    async def get_genres(self) -> list[Genre]:
        es_query = {"query": {"match_all": {}}}
        response = await self.elastic.search(index=self.index, body=es_query)
        hits = response["hits"]["hits"]
        genres = [Genre(**hit["_source"]) for hit in hits]
        return genres

    @redis_cache("genre", Genre)
    async def get_by_id(self, genre_id: str) -> Genre:
        try:
            response = await self.elastic.get(index=self.index, id=genre_id)
            return Genre(**response["_source"])
        except NotFoundError:
            logger.exception(
                "Error occurred while fetching a document '%s'",
                genre_id,
            )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
