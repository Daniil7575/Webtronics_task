import pickle
from typing import Dict, Set

from cache_base import redis_client


POST_REACTIONS_CACHE_LIFETIME_SEC = 60


async def update_cache_reactions(
    reactions: Dict[str, Set[str]], cache_key: str
) -> None:
    """
    Add to cache reactions by given key.

    :param reactions: A dictionary with reaction type as a key and
    set of reacted users id's as a value.
    """
    if any(reactions.values()):
        await redis_client.redis.set(
            cache_key,
            pickle.dumps(reactions),
            ex=POST_REACTIONS_CACHE_LIFETIME_SEC,
        )
