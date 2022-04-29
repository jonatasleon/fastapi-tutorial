"""Items schema."""
from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    """Base item schema."""

    name: str
    price: float
    description: Optional[str] = None
    is_offer: bool = False


class ItemCreate(ItemBase):
    """Item create schema."""


class ItemUpdate(BaseModel):
    """Item update schema."""

    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_offer: Optional[bool] = None


class Item(ItemBase):
    """Item schema."""

    id: int
    owner_id: int

    class Config:  # pylint: disable=too-few-public-methods, missing-class-docstring
        orm_mode = True
