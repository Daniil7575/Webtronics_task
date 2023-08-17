import pickle
from typing import Any, Dict, List, Set

import sqlalchemy as sa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import settings
from cache_base import build_key, redis_client
from posts.exceptions import empty_post_update_data, post_not_found
from posts.models import Post, Reaction, ReactionType
import logging


MAX_POSTS_COUNT_PER_PAGE = 10
logger = logging.getLogger("uvicorn")


async def create_post(post_data: dict, user_id: str, session: AsyncSession) -> Post:
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
    post = post.first()
    logger.info(f"Post {post.id} created")
    return post


async def get_post(post_id: str, session: AsyncSession) -> Post:
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


async def update_post(post_id: str, new_post_data: dict, session: AsyncSession) -> None:
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
    stmt = sa.update(Post).where(Post.id == post_id).values(**new_post_data)
    await session.execute(stmt)
    await session.commit()
    logger.info(f"Post {post_id} updated")


async def new_reaction(
    post_id: str,
    user_id: str,
    session: AsyncSession,
    reaction: ReactionType,
    reactions: Dict[str, Set[str]],
) -> None:
    """
    Add new reaction to the post.

    :param post: Post object.
    :param user_id: User id in db.
    :param session: SQLAlchemy session for querying.
    :param reaction: User's reaction on the post.
    :param reactions: A dictionary with reaction type as a key and
    set of reacted users id's as a value.
    """
    # reactions = await get_reactions(post, session)

    reactions[reaction.name].add(user_id)

    stmt = sa.insert(Reaction).values(user_id=user_id, post_id=post_id, type=reaction)
    await session.execute(stmt)
    await session.commit()
    logger.log(f"{reaction.name.capitalize()} on Post {post_id}")


async def delete_post(post_id: str, session: AsyncSession) -> None:
    """
    Delete post.

    :param post_id: Post id in db.
    :param session: SQLAlchemy session for querying.
    """
    stmt = sa.delete(Post).where(Post.id == post_id)
    await session.execute(stmt)
    await session.commit()
    logger.info(f"Post {post_id} deleted")


async def get_posts(skip: int, session: AsyncSession) -> List[Dict[str, Any]]:
    """
    Get list of posts.

    :param skip: Offset criterion in selection of posts.  Should be a multiple of a page size.
    :param session: SQLAlchemy session for querying.
    :returns: A list with posts presented in the form of dict.
    """
    # It is better not to use cached reactions, because basically (when getting post list)
    # there will be situations when there will not be cached reactions
    # for every post from the sample,
    # and then you still need to make a request to get them from the database.
    stmt = (
        sa.select(Post)
        .options(joinedload(Post.user_reactions))
        .offset(skip)
        .limit(MAX_POSTS_COUNT_PER_PAGE)
    )
    posts = (await session.scalars(stmt)).unique().all()
    posts_list = []

    for post in posts:
        post_dict = post._asdict()
        # Counter for each reaction
        post_dict["reactions"] = {react.name: 0 for react in ReactionType}
        for reaction in post.user_reactions:
            post_dict["reactions"][reaction.type.name] += 1
        posts_list.append(post_dict)

    return posts_list


async def get_reactions(post: Post, session: AsyncSession) -> Dict[str, Set[str]]:
    """
    Get reactions under specified post.

    :param post: A Post object.
    :param session: SQLAlchemy session for querying.
    :returns: A dictionary with reaction type as a key and set of reacted users id's as a value.
    """
    cached = None

    if settings.USE_CACHE:
        cache_key = build_key("reactions", str(post.id))
        cached = await redis_client.redis.get(cache_key)

    if cached is None:
        # Fetch related user_reactions from db.
        await session.refresh(post, attribute_names=["user_reactions"])
        reactions = {react_type.name: set() for react_type in ReactionType}
        # Add user_id to specific reaction under the post.
        [
            reactions[react.type.name].add(str(react.user_id))
            for react in post.user_reactions
        ]
    else:
        reactions = pickle.loads(cached)
    return reactions
