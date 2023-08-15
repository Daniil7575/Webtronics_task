from fastapi import HTTPException


# It's a bit of a strange solution to create functions that return exceptions,
# but I haven't found a better solution. If do this through inheritance from HttpException,
# then this is the class that just calls the parent constructor.
# Inheriting from Exception is also strange,
# since you would also need to make a handler and return json with status code and details,
# which HTTPException already does


def post_not_found() -> HTTPException:
    """
    Occur when post with given id is not exists in db.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        400,
        {
            "status": "error",
            "data": None,
            "details": "Post with given id is not exists.",
        },
    )


def invalid_post_id() -> HTTPException:
    """
    Occur when post id cannot be converted to UUID.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        400, {"status": "error", "data": None, "details": "Bad post id."}
    )


def user_not_owner() -> HTTPException:
    """
    Occur when user is not owner of post.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        403,
        {
            "status": "error",
            "data": None,
            "details": "You have no rights to edit this post.",
        },
    )


def empty_post_update_data() -> HTTPException:
    """
    Occur when user update data is empty.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        400,
        {
            "status": "error",
            "data": None,
            "details": "You can't update post without data.",
        },
        None,
    )


def reaction_on_yourself() -> HTTPException:
    """
    Occur when a user tries to react on their posts.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        400,
        {
            "status": "error",
            "data": None,
            "details": "You can't react on your own posts.",
        },
        None,
    )


def reaction_on_reacted_post() -> HTTPException:
    """
    Occur when a user tries to react on post that he has already reacted to.

    :returns: HTTPException with filled attributes.
    """

    return HTTPException(
        400,
        {
            "status": "error",
            "data": None,
            "details": "You have already reacted to this post.",
        },
        None,
    )
