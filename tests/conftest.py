from typing import AsyncGenerator, Callable, Awaitable
from urllib.parse import urljoin

import aiohttp
import pytest_asyncio
from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from tests.settings import test_settings


@pytest_asyncio.fixture
async def client_session() -> AsyncGenerator[ClientSession, None]:
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
async def get_request(client_session: ClientSession) -> Callable:
    async def inner(endpoint: str, params: dict = None):
        url = urljoin(test_settings.service_url, endpoint)
        params = params or {}
        async with client_session.get(url, params=params) as response:
            body = await response.json()
            return body, response.status

    return inner


@pytest_asyncio.fixture
async def redis_session() -> AsyncGenerator[Redis, None]:
    async with Redis() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def flush_cache(redis_session):
    await redis_session.flushdb()


@pytest_asyncio.fixture
async def write_data_to_es() -> (
        Callable[[list[dict], dict[str, dict]], Awaitable[None]]
):
    async def inner(test_data: list[dict], index_mapping: dict[str, dict]):
        index = index_mapping.get("index_name")
        schema = index_mapping.get("index_schema")
        bulk_query: list[dict] = []
        for row in test_data:
            data = {"_index": index, "_id": row["id"]}
            data.update({"_source": row})
            bulk_query.append(data)

        es_client = AsyncElasticsearch(
            hosts=[
                f"{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}"
            ]
        )

        try:
            if await es_client.indices.exists(index=index):
                await es_client.indices.delete(index=index)
            await es_client.indices.create(index=index, body=schema)
            await async_bulk(client=es_client, actions=bulk_query)
            await es_client.indices.refresh(index=index)
        finally:
            await es_client.close()

    return inner
