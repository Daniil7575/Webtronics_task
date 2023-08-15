from typing import Optional

from pydantic import BaseModel, validator


class CreatePost(BaseModel):
    title: str
    description: Optional[str]


class EditPost(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    # Remove unnecessary spaces at the beginning and at the end of a title/description
    @validator("title", "description")
    def validate_whitespaces(cls, value):
        if value:
            value = tmp if (tmp := value.strip()) else None
        return value
