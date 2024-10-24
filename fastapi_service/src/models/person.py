from uuid import UUID

from pydantic import BaseModel, Field

from fastapi_service.src.models.person_film_work import PersonFilmWork


class Person(BaseModel):
    id: UUID = Field(alias="uuid")
    name: str = Field(alias="full_name")

    class Config:
        populate_by_name = True


class PersonWithFilms(Person):
    films: list[PersonFilmWork] | None = []
