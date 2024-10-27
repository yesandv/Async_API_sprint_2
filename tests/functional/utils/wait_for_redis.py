import time

import redis

from tests.settings import test_settings

if __name__ == "__main__":
    redis_client = redis.Redis(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
