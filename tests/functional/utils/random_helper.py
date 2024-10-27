import random
import uuid

from faker import Faker


def generate_genres(count: int = 1) -> list[dict]:
    return [
        {
            "id": str(uuid.uuid4()),
            "name": Faker().word(),
        }
        for _ in range(count)
    ]


def generate_persons(count: int = 1) -> list[dict]:
    return [
        {
            "id": str(uuid.uuid4()),
            "name": Faker().name(),
        }
        for _ in range(count)
    ]


def generate_films(
        count: int = 1,
        with_actors: bool = False,
        with_writers: bool = False,
        with_directors: bool = False,
) -> list[dict]:
    return [
        {
            "id": str(uuid.uuid4()),
            "title": Faker().word(),
            "imdb_rating": round(random.uniform(0.0, 10.0), 1),
            "description": Faker().sentence(),
            "genres": ", ".join(
                (Faker().word() for _ in range(random.randint(1, 5)))
            ),
            "actors": (
                generate_persons(random.randint(1, 5)) if with_actors else []
            ),
            "writers": (
                generate_persons(random.randint(1, 5)) if with_writers else []
            ),
            "directors": (
                generate_persons(random.randint(1, 5))
                if with_directors
                else []
            ),
        }
        for _ in range(count)
    ]
