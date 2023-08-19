from uuid import UUID, uuid4
import enum
from datetime import datetime
from typing import List, Set

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class ReactionType(enum.Enum):
    dislike = 0
    like = 1


class Reaction(Base):
    __tablename__ = "reaction"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    post_id: Mapped[UUID] = mapped_column(ForeignKey("post.id", ondelete="cascade"), primary_key=True)
    type_: Mapped[Enum[ReactionType]] = mapped_column(Enum(ReactionType))


class Post(Base):
    __tablename__ = "post"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    creation_date: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    last_update_date: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
    user_reactions: Mapped[Set["Reaction"]] = relationship()
