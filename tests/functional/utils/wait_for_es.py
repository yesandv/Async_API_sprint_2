import time

from elasticsearch import Elasticsearch

from tests.settings import test_settings

if __name__ == "__main__":
    es_client = Elasticsearch(
        hosts=[
            f"{test_settings.es_schema}://{test_settings.es_host}:{test_settings.es_port}"
        ]
    )
    while True:
        if es_client.ping():
            break
        time.sleep(1)
