from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from tests.functional.testdata import film_schema, genre_schema, person_schema


class TestSettings(BaseSettings):
    es_schema: str = "http"
    es_host: str = Field("127.0.0.1", alias="ELASTIC_HOST")
    es_port: int = Field(9200, alias="ELASTIC_PORT")
    es_film_mapping: dict = film_schema.mapping
    es_genre_mapping: dict = genre_schema.mapping
    es_person_mapping: dict = person_schema.mapping
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    service_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


test_settings = TestSettings()
