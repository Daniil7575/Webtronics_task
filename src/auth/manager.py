import logging
import uuid
from typing import Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, UUIDIDMixin

import settings
from auth.models import User
from auth.utils import get_user_db


logger = logging.getLogger("uvicorn")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        logger.info(f"User {user.id} has registered.")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        logger.info(f"User {user.id} has logged in.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
