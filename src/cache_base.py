from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import settings


class RedisClient():
    def __init__(self, url: str) -> None:
        self.redis = None
        self.url = url
    
    async def connect_redis(self) -> None:
        self.redis = await aioredis.from_url(self.url, encoding="utf8")
        FastAPICache.init(RedisBackend(self.redis), prefix="fastapi-cache")


def build_key(*args) -> str:
    """
    Builds a key from passed arguments and a colon between them.

    :param args: An arguments that the key will consist of.
    :returns: Key for caching in redis.
    :example: "arg1:arg2:arg3".
    """
    return ":".join(args)


redis_client = RedisClient(settings.REDIS_URL)
