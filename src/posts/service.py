from typing import Any, Dict, List
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from posts.exceptions import (
    empty_post_update_data,
    post_not_found,
    reaction_on_reacted_post,
)
from posts.models import Post, Reaction, ReactionType


MAX_POSTS_COUNT_PER_PAGE = 10


async def create_post(post_data: dict, user_id: UUID, session: AsyncSession) -> Post:
    """
    Creates new post and returns new post id and title if insertion is successfull.

    :param post_data: A dict with user filled fields.
    :param user_id: User id in db.
    :param session: SQLAlchemy session for querying.
    :returns: New post object with only id and title fields.
    """
    stmt = (
        sa.insert(Post)
        .values(owner_id=user_id, **post_data)
        .returning(Post.id, Post.title)
    )
    post = await session.execute(stmt)
    await session.commit()
    return post.first()


async def get_post(post_id: UUID, session: AsyncSession) -> Post:
    """
    Get a specifiс Post.

    :param post_id: Post id in db.
    :param session: SQLAlchemy session for querying.
    :raises HTTPException: The post does not exist.
    :returns: A Post object.
    """

    stmt = sa.select(Post).where(Post.id == post_id)
    try:
        post = (await session.execute(stmt)).scalar_one()
    except NoResultFound:
        raise post_not_found()
    return post


async def update_post(post: Post, new_post_data: dict, session: AsyncSession) -> None:
    """
    Updates post.

    :param post: Post object.
    :param new_post_data: A dictionary with updatable user filled dields.
    :param session: SQLAlchemy session for querying.
    :raises HTTPException: The User did not provide any data.
    """
    # Checking if user given data is empty
    if not new_post_data:
        raise empty_post_update_data()
    stmt = sa.update(Post).where(Post.id == post.id).values(**new_post_data)
    await session.execute(stmt)
    await session.commit()


async def new_reaction(
    post: Post, user_id: UUID, session: AsyncSession, reaction: ReactionType
) -> None:
    """
    Add new reaction to the post.

    :param post: Post object.
    :param user_id: User id in db.
    :param session: SQLAlchemy session for querying.
    :param reaction: User's reaction on the post.
    :raises HTTPException: The User already reacted on the Post.
    """
    new_reaction_pk = f"{user_id}__{post.id}"
    # Checking whether the user reacted to this post

    # Convert Reaction objects to str "{user_id}__{post_id}"
    # for checking existence in the reactions under the post
    # also for caching
    reacts_pks = set(
        map(lambda obj: f"{obj.user_id}__{obj.post_id}", post.user_reactions)
    )
    if new_reaction_pk in reacts_pks:
        raise reaction_on_reacted_post()
    stmt = sa.insert(Reaction).values(user_id=user_id, post_id=post.id, type=reaction)
    await session.execute(stmt)
    await session.commit()


async def delete_post(post_id: UUID, session: AsyncSession) -> None:
    """
    Delete post.

    :param post_id: Post id in db.
    :param session: SQLAlchemy session for querying.
    """

    stmt = sa.delete(Post).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()


async def get_posts(skip: int, session: AsyncSession) -> List[Dict[str, Any]]:
    """
    Get list of posts.

    :param skip: Offset criterion in selection of posts.  Should be a multiple of a page size.
    :param session: SQLAlchemy session for querying.
    :returns: A list with posts presented in the form of dict.
    """
    stmt = sa.select(Post).offset(skip).limit(MAX_POSTS_COUNT_PER_PAGE)
    posts = (await session.scalars(stmt)).all()
    posts_list = []

    for post in posts:
        post_dict = post._asdict()
        # Counter for each reaction
        post_dict["reactions"] = {react.name: 0 for react in ReactionType}
        for reaction in post.user_reactions:
            post_dict["reactions"][reaction.type.name] += 1
        posts_list.append(post_dict)

    return posts_list
