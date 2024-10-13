from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import ValidationError
from redis.asyncio import Redis

from src.core import config
from src.core.logger import logger
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import FilmDetails, Film
from src.models.person_film_work import PersonFilmWork, ROLES
from src.services.genre import GenreService, get_genre_service


class FilmService:
    def __init__(
            self,
            redis: Redis,
            elastic: AsyncElasticsearch,
            genre_service: GenreService,
    ):
        self.redis = redis
        self.elastic = elastic
        self.genre_service = genre_service
        self.index = config.ELASTIC_FILM_INDEX

    async def get_by_id(self, film_id: str) -> FilmDetails:
        try:
            response = await self.elastic.get(index=self.index, id=film_id)
            film_data = response["_source"]
            _genres = [
                await self.genre_service.get_by_name(genre_name)
                for genre_name in film_data["genres"]
            ]
            film_data["genres"] = _genres
            return FilmDetails(**film_data)
        except NotFoundError:
            logger.exception(
                "Error occurred while fetching a document '%s'",
                film_id,
            )
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
        response = await self.elastic.search(index=self.index, body=es_query)
        hits = response["hits"]["hits"]
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
        response = await self.elastic.search(index=self.index, body=es_query)
        hits = response["hits"]["hits"]
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
        response = await self.elastic.search(index=self.index, body=es_query)
        hits = response["hits"]["hits"]
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
                    PersonFilmWork(id=film_data["id"], roles=_roles)
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
        response = await self.elastic.search(index=self.index, body=es_query)
        return [Film(**hit["_source"]) for hit in response["hits"]["hits"]]


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        genre_service: GenreService = Depends(get_genre_service),
) -> FilmService:
    return FilmService(redis, elastic, genre_service)
