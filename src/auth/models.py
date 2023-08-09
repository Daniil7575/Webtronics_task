from typing import List
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean

from database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
        """
            User model:
                username: Mapped[str]
                ---------------------------
                fastapi_users default columns:
                id: Mapped[UUID_ID]
                email: Mapped[str]
                hashed_password: Mapped[str]
                is_active: Mapped[bool]
                is_superuser: Mapped[bool]
                is_verified: Mapped[bool]
            ---------------------------
            __tablename__ = "user"
        """
        username: Mapped[str] = mapped_column(
            String(length=100), unique=True, index=True, nullable=False
        )
        # id: Mapped[UUID_ID] = mapped_column(
        #     GUID, primary_key=True, default=uuid.uuid4
        # )
        # email: Mapped[str] = mapped_column(
        #     String(length=320), unique=True, index=True, nullable=False
        # )
        # hashed_password: Mapped[str] = mapped_column(
        #     String(length=1024), nullable=False
        # )
        # is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
        # is_superuser: Mapped[bool] = mapped_column(
        #     Boolean, default=False, nullable=False
        # )
        # is_verified: Mapped[bool] = mapped_column(
        #     Boolean, default=False, nullable=False
        # )
