"""User schemas."""
from typing import List, Optional

from pydantic import BaseModel

from .item import Item


class UserBase(BaseModel):
    """Base user schema."""

    id: int = None
    name: str
    email: str
    is_active: bool = True


class UserCreate(UserBase):
    """User create schema."""

    password: str


class User(UserBase):
    """User schema."""

    password: str
    items: Optional[List[Item]] = None

    class Config:  # pylint: disable=too-few-public-methods, missing-class-docstring
        orm_mode = True


class UserShow(UserBase):
    """User show schema."""

    id: int

    class Config:  # pylint: disable=too-few-public-methods, missing-class-docstring
        orm_mode = True
