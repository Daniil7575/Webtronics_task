from uuid import UUID

from fastapi import Depends
from auth.models import User
from database import get_async_session
from auth.base_config import current_user
from sqlalchemy.ext.asyncio import AsyncSession

from posts.exceptions import invalid_post_id


def validate_id(post_id: str) -> UUID:
    """
    Validate id.

    :param post_id: Post id in db.
    :raises HTTPException: Post id cannot be converted to UUID.
    """
    print(post_id)
    try:
        # Trying to convert given post_id to UUID
        post_id = UUID(post_id)
    except ValueError:
        raise invalid_post_id()
    return post_id


async def reaction_common_params(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post_id: UUID = Depends(validate_id),
):
    return {"session": session, "user": user, "post_id": post_id}