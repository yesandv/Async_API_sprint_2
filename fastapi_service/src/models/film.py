from uuid import UUID

from pydantic import BaseModel, Field

from fastapi_service.src.models.genre import Genre
from fastapi_service.src.models.person import Person


class Film(BaseModel):
    id: UUID = Field(alias="uuid")
    title: str
    imdb_rating: float | None

    class Config:
        populate_by_name = True


class FilmDetails(Film):
    description: str | None
    genres: list[Genre] | None
    actors: list[Person] | None
    writers: list[Person] | None
    directors: list[Person] | None
