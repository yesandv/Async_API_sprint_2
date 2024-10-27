import time

from elasticsearch import Elasticsearch

from tests.settings import test_settings

if __name__ == "__main__":
    es_client = Elasticsearch(hosts=test_settings.es_host)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
