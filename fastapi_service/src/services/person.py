from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from fastapi_service.src.core import config
from fastapi_service.src.core.logger import logger
from fastapi_service.src.db.elastic import get_elastic
from fastapi_service.src.db.redis import get_redis, redis_cache
from fastapi_service.src.models.film import Film
from fastapi_service.src.models.person import PersonWithFilms
from fastapi_service.src.services.film import FilmService, get_film_service


class PersonService:
    def __init__(
            self,
            redis: Redis,
            elastic: AsyncElasticsearch,
            film_service: FilmService,
    ):
        self.redis = redis
        self.elastic = elastic
        self.film_service = film_service
        self.index = config.ELASTIC_PERSON_INDEX

    async def search(
            self, query: str, page_number: int, page_size: int
    ) -> list[PersonWithFilms]:
        es_query = {
            "query": {
                "match": {
                    "name": query,
                }
            },
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }
        response = await self.elastic.search(index=self.index, body=es_query)
        hits = response["hits"]["hits"]
        persons = [PersonWithFilms(**hit["_source"]) for hit in hits]
        for person in persons:
            person_film_works = await self.film_service.get_by_person_name(
                person.name
            )
            person.films = person_film_works
        return persons

    @redis_cache("person", PersonWithFilms)
    async def get_by_id(self, person_id: str) -> PersonWithFilms:
        try:
            response = await self.elastic.get(index=self.index, id=person_id)
            person = PersonWithFilms(**response["_source"])
            person.films = await self.film_service.get_by_person_name(
                person.name
            )
            return person
        except NotFoundError:
            logger.exception(
                "Error occurred while fetching a document '%s'",
                person_id,
            )

    @redis_cache("pfw", Film)
    async def get_film_works_by_person_id(self, person_id: str) -> list[Film]:
        return await self.film_service.get_by_person_id(person_id)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        film_service: FilmService = Depends(get_film_service),
) -> PersonService:
    return PersonService(redis, elastic, film_service)
