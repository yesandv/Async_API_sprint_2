from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi_service.src.core.logger import logger
from fastapi_service.src.db.search_repository import SearchRepository

es: AsyncElasticsearch | None = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class ElasticsearchRepository(SearchRepository):
    def __init__(self, elastic: AsyncElasticsearch, index: str):
        self.elastic = elastic
        self.index = index

    async def search(self, body: dict) -> list[dict]:
        response = await self.elastic.search(index=self.index, body=body)
        return response["hits"]["hits"]

    async def get(self, doc_id: str) -> dict:
        try:
            response = await self.elastic.get(index=self.index, id=doc_id)
            return response["_source"]
        except NotFoundError:
            logger.exception(
                "Error occurred while fetching a document '%s'", doc_id
            )
