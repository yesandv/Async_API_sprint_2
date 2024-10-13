from uuid import UUID

from pydantic import BaseModel, Field


class Person(BaseModel):
    uuid: UUID = Field(alias="id")
    full_name: str = Field(alias="name")
