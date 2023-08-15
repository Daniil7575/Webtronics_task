from fastapi import Depends, FastAPI

from auth.base_config import auth_backend, current_user, fastapi_users
from auth.schemas import UserCreate, UserRead
from posts.router import router

import logging

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

app.include_router(
    router
)