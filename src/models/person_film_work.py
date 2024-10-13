from uuid import UUID

from pydantic import BaseModel, Field

ROLES = ["actors", "directors", "writers"]


class PersonFilmWork(BaseModel):
    uuid: UUID = Field(alias="id")
    roles: list[str]
