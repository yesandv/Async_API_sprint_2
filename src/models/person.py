from uuid import UUID

from pydantic import BaseModel, Field

from src.models.person_film_work import PersonFilmWork


class Person(BaseModel):
    uuid: UUID = Field(alias="id")
    full_name: str = Field(alias="name")


class PersonWithFilms(Person):
    films: list[PersonFilmWork] | None = []
