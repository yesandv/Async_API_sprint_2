from uuid import UUID

from pydantic import BaseModel, Field

from src.models.genre import Genre
from src.models.person import Person


class Film(BaseModel):
    uuid: UUID = Field(alias="id")
    title: str
    imdb_rating: float | None


class FilmDetails(Film):
    description: str | None
    genres: list[Genre] | None
    actors: list[Person] | None
    writers: list[Person] | None
    directors: list[Person] | None
