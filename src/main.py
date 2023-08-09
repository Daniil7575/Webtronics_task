from fastapi import FastAPI, Depends

from auth.base_config import fastapi_users, auth_backend
from auth.schemas import UserRead, UserCreate
from auth.models import User
from auth.base_config import current_user


app = FastAPI(title="Webtronics task")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

