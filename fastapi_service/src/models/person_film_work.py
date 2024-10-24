from uuid import UUID

from pydantic import BaseModel, Field

ROLES = ["actors", "directors", "writers"]


class PersonFilmWork(BaseModel):
    id: UUID = Field(alias="uuid")
    roles: list[str]

    class Config:
        populate_by_name = True
