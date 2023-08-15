from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import current_user
from auth.models import User
from database import get_async_session
from posts import service
from posts.dependencies import reaction_common_params, validate_id
from posts.exceptions import reaction_on_yourself, user_not_owner
from posts.models import ReactionType
from posts.schemas import CreatePost, EditPost

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("")
async def get_posts(session: AsyncSession = Depends(get_async_session), skip: int = 0):
    posts = await service.get_posts(skip, session)
    return {"status": "success", "data": posts, "details": None}


@router.post("")
async def create_post(
    post_data: CreatePost,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    post = await service.create_post(post_data.model_dump(), user.id, session)
    print(f'Post "{post.title}" with id - {post.id} was created')
    return {
        "status": "success",
        "data": post.id,
        "details": f'Post "{post.title}" was created!',
    }


@router.patch("/{post_id}")
async def edit_post(
    edit_post_data: EditPost,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post_id: UUID = Depends(validate_id),
):
    post = await service.get_post(post_id, session)
    if post.owner_id != user.id:
        raise user_not_owner()
    edit_post_dict = edit_post_data.model_dump(exclude_none=True)
    await service.update_post(post, edit_post_dict, session)

    return {
        "status": "success",
        "data": None,
        "details": "Post has been successfully updated!",
    }


@router.delete("/{post_id}")
async def delete_post(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post_id: UUID = Depends(validate_id),
):
    post = await service.get_post(post_id, session)
    if post.owner_id != user.id:
        raise user_not_owner()
    await service.delete_post(post_id, session)
    return {
        "status": "success",
        "data": None,
        "details": "Post has been successfully deleted!",
    }


@router.get("/{post_id}")
async def get_post(
    session: AsyncSession = Depends(get_async_session),
    post_id: UUID = Depends(validate_id),
):
    post = await service.get_post(post_id, session)
    return {"status": "success", "data": post._asdict(), "details": None}


@router.post("/{post_id}/like")
async def like_post(params: Dict[str, Any] = Depends(reaction_common_params)):
    return await react_on_post(**params, reaction=ReactionType.like)


@router.post("/{post_id}/dislike")
async def like_post(params: Dict[str, Any] = Depends(reaction_common_params)):
    return await react_on_post(**params, reaction=ReactionType.dislike)


async def react_on_post(
    session: AsyncSession, user: User, post_id: UUID, reaction: ReactionType
):
    post = await service.get_post(post_id, session)
    if post.owner_id == user.id:
        raise reaction_on_yourself()
    await service.new_reaction(post, user.id, session, reaction)
    return {
        "status": "success",
        "data": None,
        "details": f"Successfully {reaction.name} post!",
    }
