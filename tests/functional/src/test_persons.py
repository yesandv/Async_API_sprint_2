import uuid
from http import HTTPStatus
from random import choice

import pytest

from tests.functional.utils.random_helper import (
    generate_persons,
    generate_films,
)
from tests.settings import test_settings


class TestV1Persons:
    path = "/api/v1/persons"

    @pytest.mark.asyncio
    async def test_v1_persons_search(
            self, flush_cache, write_data_to_es, get_request
    ):
        film_data = (film,) = generate_films(with_actors=True)
        actor_data = film["actors"]
        actor = choice(actor_data)
        await write_data_to_es(film_data, test_settings.es_film_mapping)
        await write_data_to_es(actor_data, test_settings.es_person_mapping)

        params = {"query": actor["name"], "page_number": 1, "page_size": 1}
        response, status = await get_request(
            self.path + "/search", params=params
        )

        assert status == HTTPStatus.OK
        assert len(response) == 1
        actual_actor = response[0]
        assert actual_actor["uuid"] == actor["id"]
        assert actual_actor["full_name"] == actor["name"]
        assert film["id"] in [film["uuid"] for film in actual_actor["films"]]
        assert "actor" in [
            role for film in actual_actor["films"] for role in film["roles"]
        ]

    @pytest.mark.asyncio
    async def test_v1_persons_search_no_films(
            self, flush_cache, write_data_to_es, get_request
    ):
        person_data = (person,) = generate_persons()
        first_name = person["name"].split()[0]
        await write_data_to_es(person_data, test_settings.es_person_mapping)

        params = {"query": first_name, "page_number": 1, "page_size": 1}
        response, status = await get_request(
            self.path + "/search", params=params
        )

        assert status == HTTPStatus.OK
        assert len(response) == 1
        actual_person = response[0]
        assert actual_person["uuid"] == person["id"]
        assert actual_person["full_name"] == person["name"]
        assert not actual_person["films"]

    @pytest.mark.asyncio
    async def test_v1_persons_search_pagination(
        self, flush_cache, write_data_to_es, get_request
    ):
        person_data = generate_persons(64)
        new_first_name = "John"
        for person in person_data:
            first_name, *last_name = person["name"].split()
            person["name"] = f"{new_first_name} {' '.join(last_name)}"
        await write_data_to_es(person_data, test_settings.es_person_mapping)

        params = {"query": new_first_name, "page_number": 1, "page_size": 100}
        response, _ = await get_request(self.path + "/search", params=params)

        assert (total_count := len(response)) == len(person_data)

        person_ids = []
        page_number, page_size = 1, 10
        total_retrieved = 0

        while total_retrieved < total_count:
            params = {
                "query": new_first_name,
                "page_number": page_number,
                "page_size": page_size,
            }
            response, _ = await get_request(
                self.path + "/search", params=params
            )

            assert len(response) == min(
                page_size, total_count - total_retrieved
            )

            page_number += 1
            total_retrieved += len(response)
            person_ids += [person["uuid"] for person in response]

        assert total_retrieved == total_count
        assert set(person_ids) == {person["id"] for person in person_data}

    @pytest.mark.asyncio
    async def test_v1_persons_by_person_id(
            self, flush_cache, write_data_to_es, get_request
    ):
        person_data = (person,) = generate_persons()
        film_data = generate_films(2)
        for film in film_data:
            film["directors"] = [person]
        person_id = person["id"]
        await write_data_to_es(film_data, test_settings.es_film_mapping)
        await write_data_to_es(person_data, test_settings.es_person_mapping)

        response, status = await get_request(self.path + f"/{person_id}")

        assert status == HTTPStatus.OK
        assert response["uuid"] == person_id
        assert response["full_name"] == person["name"]
        assert {film["uuid"] for film in response["films"]} == {
            film["id"] for film in film_data
        }
        assert {
                   role for film in response["films"] for role in film["roles"]
               } == {"director"}

    @pytest.mark.asyncio
    async def test_v1_persons_by_invalid_person_id(
            self, flush_cache, get_request
    ):
        person_id = str(uuid.uuid4())

        response, status = await get_request(self.path + f"/{person_id}")

        assert status == HTTPStatus.NOT_FOUND
        assert response["detail"] == "Person was not found"

    @pytest.mark.asyncio
    async def test_v1_persons_films_by_person_id(
            self, flush_cache, write_data_to_es, get_request
    ):
        person_data = (person,) = generate_persons()
        film_data = generate_films(3)
        for film in film_data:
            film["writers"] = [person]
        person_id = person["id"]
        await write_data_to_es(film_data, test_settings.es_film_mapping)
        await write_data_to_es(person_data, test_settings.es_person_mapping)

        response, status = await get_request(self.path + f"/{person_id}/films")

        assert status == HTTPStatus.OK
        assert len(response) == len(film_data)
        assert {film["uuid"] for film in response} == {
            film["id"] for film in film_data
        }
        assert {film["title"] for film in response} == {
            film["title"] for film in film_data
        }
        assert {film["imdb_rating"] for film in response} == {
            film["imdb_rating"] for film in film_data
        }
