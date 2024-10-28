import json
from functools import wraps
from typing import Callable, Any

from redis.asyncio import Redis

from fastapi_service.src.core.encoder import UUIDEncoder

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


def redis_cache(prefix: str, model: Any, ttl: int = 1200):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self, key = args
            cache_key = f"{prefix}:{key}"

            cached_result = await self.redis.get(cache_key)
            if cached_result:
                parsed_result = json.loads(cached_result.decode("utf-8"))
                if isinstance(parsed_result, list):
                    return [model(**result) for result in parsed_result]
                return model(**parsed_result)

            result = await func(*args, **kwargs)

            if result:
                if isinstance(result, list):
                    serialized_data = json.dumps(
                        [item.dict() for item in result], cls=UUIDEncoder
                    )
                else:
                    serialized_data = json.dumps(
                        result.dict(), cls=UUIDEncoder
                    )
                await self.redis.set(
                    cache_key,
                    serialized_data,
                    ex=ttl,
                )

            return result

        return wrapper

    return decorator
