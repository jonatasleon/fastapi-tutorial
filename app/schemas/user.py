"""User schemas."""
from typing import List

from pydantic import BaseModel

from .item import Item


class UserBase(BaseModel):
    """Base user schema."""

    name: str
    email: str
    is_active: bool = True


class UserCreate(UserBase):
    """User create schema."""

    password: str


class User(UserBase):
    """User schema."""

    id: int
    password: str
    items: List[Item] = []

    class Config:  # pylint: disable=too-few-public-methods, missing-class-docstring
        orm_mode = True


class UserShow(UserBase):
    """User show schema."""

    id: int

    class Config:  # pylint: disable=too-few-public-methods, missing-class-docstring
        orm_mode = True
