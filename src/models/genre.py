from uuid import UUID

from pydantic import BaseModel, Field


class Genre(BaseModel):
    id: UUID = Field(alias="uuid")
    name: str

    class Config:
        populate_by_name = True
