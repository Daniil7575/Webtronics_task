import logging

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import uvicorn

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from posts.router import router
from cache_base import redis_client


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app = FastAPI(title="Webtronics task")

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await redis_client.connect_redis()
    # print(await redis_client.redis.get("a"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
