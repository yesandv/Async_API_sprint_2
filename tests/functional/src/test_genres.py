import uuid
from http import HTTPStatus

import pytest

from tests.functional.utils.random_helper import generate_genres
from tests.settings import test_settings


class TestV1Genres:
    path = "/api/v1/genres"

    @pytest.mark.asyncio
    async def test_v1_genres(self, flush_cache, write_data_to_es, get_request):
        test_data = generate_genres(10)
        await write_data_to_es(test_data, test_settings.es_genre_mapping)

        response, status = await get_request(self.path + "/")

        assert status == HTTPStatus.OK
        assert len(response) == len(test_data)
        assert {actual_genre["uuid"] for actual_genre in response} == {
            genre["id"] for genre in test_data
        }
        assert {actual_genre["name"] for actual_genre in response} == {
            genre["name"] for genre in test_data
        }

    @pytest.mark.asyncio
    async def test_v1_genres_by_genre_id(
            self, flush_cache, write_data_to_es, get_request
    ):
        test_data = (genre,) = generate_genres()
        await write_data_to_es(test_data, test_settings.es_genre_mapping)
        genre_id = genre["id"]

        response, status = await get_request(self.path + f"/{genre_id}")

        assert status == HTTPStatus.OK
        assert response["uuid"] == genre_id
        assert response["name"] == genre["name"]

    @pytest.mark.asyncio
    async def test_v1_genres_by_invalid_genre_id(
            self, flush_cache, get_request
    ):
        genre_id = str(uuid.uuid4())

        response, status = await get_request(self.path + f"/{genre_id}")

        assert status == HTTPStatus.NOT_FOUND
        assert response["detail"] == "Genre was not found"
