from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import ValidationError
from redis.asyncio import Redis

from fastapi_service.src.core import config
from fastapi_service.src.core.logger import logger
from fastapi_service.src.db.elastic import (
    get_elastic,
    ElasticsearchRepository,
)
from fastapi_service.src.db.redis import get_redis, redis_cache
from fastapi_service.src.models.film import FilmDetails, Film
from fastapi_service.src.models.genre import Genre
from fastapi_service.src.models.person_film_work import PersonFilmWork, ROLES
from fastapi_service.src.services.genre import GenreService, get_genre_service


class FilmService:
    def __init__(
            self,
            redis: Redis,
            elastic: ElasticsearchRepository,
            genre_service: GenreService,
    ):
        self.redis = redis
        self.elastic = elastic
        self.genre_service = genre_service

    @redis_cache("film", model=FilmDetails)
    async def get_by_id(self, film_id: str) -> FilmDetails:
        try:
            film_data = await self.elastic.get(doc_id=film_id)
            if film_data:
                _genres = [
                    await self.genre_service.get_by_name(genre_name)
                    for genre_name in film_data["genres"]
                ]
                film_data["genres"] = _genres
                return FilmDetails(**film_data)
        except ValidationError:
            logger.exception(
                "Check a data structure of the document '%s'",
                film_id,
            )

    async def search(
            self, query: str, page_number: int, page_size: int
    ) -> list[Film]:
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                }
            },
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }
        hits = await self.elastic.search(body=es_query)
        films = [Film(**hit["_source"]) for hit in hits]
        return films

    async def get_films(
            self,
            sort: str,
            page_number: int,
            page_size: int,
            genre_id: str = None,
    ) -> list[Film]:
        sort_field = sort.lstrip("-")
        sort_order = "desc" if sort.startswith("-") else "asc"
        es_query = {
            "sort": [{sort_field: {"order": sort_order}}],
            "from": (page_number - 1) * page_size,
            "size": page_size,
        }
        if genre_id:
            genre = await self.genre_service.get_by_id(genre_id)
            es_query["query"] = {"match": {"genres": genre.name}}
        hits = await self.elastic.search(body=es_query)
        films = [Film(**hit["_source"]) for hit in hits]
        return films

    async def get_by_person_name(
            self, person_name: str
    ) -> list[PersonFilmWork]:
        person_film_works = []
        should_query = [
            {
                "nested": {
                    "path": role,
                    "query": {"match": {f"{role}.name": person_name}},
                }
            }
            for role in ROLES
        ]
        es_query = {
            "query": {
                "bool": {"should": should_query, "minimum_should_match": 1}
            }
        }
        hits = await self.elastic.search(body=es_query)
        for hit in hits:
            film_data = hit["_source"]
            _roles = []
            for role in ROLES:
                if any(
                        data["name"] == person_name
                        for data in film_data.get(role, [])
                ):
                    _roles.append(role.rstrip("s"))
            if _roles:
                person_film_works.append(
                    PersonFilmWork(uuid=film_data["id"], roles=_roles)
                )
        return person_film_works

    async def get_by_person_id(self, person_id: str) -> list[Film]:
        should_query = [
            {
                "nested": {
                    "path": role,
                    "query": {"match": {f"{role}.id": person_id}},
                }
            }
            for role in ROLES
        ]
        es_query = {
            "query": {
                "bool": {"should": should_query, "minimum_should_match": 1}
            }
        }
        hits = await self.elastic.search(body=es_query)
        return [Film(**hit["_source"]) for hit in hits]

    async def get_by_genres(self, genres: list[Genre]) -> list[Film]:
        es_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"genres": genre.name}} for genre in genres
                    ]
                }
            }
        }
        hits = await self.elastic.search(body=es_query)
        films = [Film(**hit["_source"]) for hit in hits]
        return films


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        genre_service: GenreService = Depends(get_genre_service),
) -> FilmService:
    return FilmService(
        redis,
        ElasticsearchRepository(elastic, config.ELASTIC_FILM_INDEX),
        genre_service
    )
