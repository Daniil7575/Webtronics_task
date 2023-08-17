from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI

import settings
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from cache_base import redis_client
from posts.router import router


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=settings.LOG_CONFIG)
