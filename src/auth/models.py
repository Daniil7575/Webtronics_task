from typing import List

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User model:
        :param username: User name to display.
    ---------------------------
    fastapi_users default columns:
        :param id: Id.
        :param email: Emal addres.
        :param hashed_password: Hashed password.
        :param is_active: Is active flag.
        :param is_superuser: Is superuser flag.
        :param is_verified: Is verified flag.
    ---------------------------
    Table name - "user"
    """

    username: Mapped[str] = mapped_column(
        String(length=100), nullable=False
    )
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="owner")
