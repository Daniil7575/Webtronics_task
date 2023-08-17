from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from posts import service
from posts.cache import update_cache_reactions
from posts.dependencies import reaction_common_params, validate_id
from posts.exceptions import (
    reaction_on_reacted_post,
    reaction_on_yourself,
    user_not_owner,
)
from posts.models import ReactionType
from posts.schemas import CreatePost, EditPost
from cache_base import build_key


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def get_posts(session: AsyncSession = Depends(get_async_session), skip: int = 0):
    """Get post list."""
    posts = await service.get_posts(skip, session)
    return {"status": "success", "data": posts, "details": None}


@router.post("")
async def create_post(
    post_data: CreatePost,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Create a new post."""
    post = await service.create_post(post_data.model_dump(), user.id, session)
    return {
        "status": "success",
        "data": post.id,
        "details": f'Post "{post.title}" was created!',
    }


@router.get("/{post_id}")
async def get_post(
    session: AsyncSession = Depends(get_async_session),
    post_id: str = Depends(validate_id),
):
    """Get specific post."""
    post = await service.get_post(post_id, session)

    post_dict = post._asdict()
    post_dict["reactions"] = await service.get_reactions(post, session)

    if settings.USE_CACHE:
        # Refresh cache.
        await update_cache_reactions(
            post_dict["reactions"], cache_key=build_key("reactions", str(post.id))
        )

    return {"status": "success", "data": post_dict, "details": None}


@router.patch("/{post_id}")
async def edit_post(
    edit_post_data: EditPost,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post_id: str = Depends(validate_id),
):
    """Update post."""
    post = await service.get_post(post_id, session)

    if post.owner_id != user.id:
        raise user_not_owner()
    edit_post_dict = edit_post_data.model_dump(exclude_none=True)
    await service.update_post(str(post.id), edit_post_dict, session)

    return {
        "status": "success",
        "data": None,
        "details": "Post has been successfully updated!",
    }


@router.delete("/{post_id}")
async def delete_post(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post_id: str = Depends(validate_id),
):
    """Delete post."""
    post = await service.get_post(post_id, session)
    if post.owner_id != user.id:
        raise user_not_owner()
    await service.delete_post(post_id, session)
    return {
        "status": "success",
        "data": None,
        "details": "Post has been successfully deleted!",
    }


@router.post("/{post_id}/like")
async def like_post(params: Dict[str, Any] = Depends(reaction_common_params)):
    """Add like to a post."""
    return await react_on_post(**params, reaction=ReactionType.like)


@router.post("/{post_id}/dislike")
async def dislike_post(params: Dict[str, Any] = Depends(reaction_common_params)):
    """Add dislike to a post."""
    return await react_on_post(**params, reaction=ReactionType.dislike)


async def react_on_post(
    session: AsyncSession, user: User, post_id: str, reaction: ReactionType
):
    """
    Add reaction to a post.

    :param session: SQLAlchemy session for querying.
    :param user: A User object.
    :param post_id: Post id in db.
    :param reaction: User's reaction on the post.
    """
    user_id = str(user.id)
    post = await service.get_post(post_id, session)

    if post.owner_id == user_id:
        raise reaction_on_yourself()

    reactions = await service.get_reactions(post, session)
    # Checking whether the user reacted to this post.
    for reacted_users in reactions.values():
        if user_id in reacted_users:
            raise reaction_on_reacted_post()

    await service.new_reaction(str(post.id), user_id, session, reaction, reactions)

    if settings.USE_CACHE:
        # Modify cache.
        await update_cache_reactions(
            reactions, cache_key=build_key("reactions", post_id)
        )

    return {
        "status": "success",
        "data": None,
        "details": f"Successfully '{reaction.name}' post!",
    }
