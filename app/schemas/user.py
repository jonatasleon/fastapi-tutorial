from typing import List

from pydantic import BaseModel

from .item import Item


class UserBase(BaseModel):
    name: str
    email: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    password: str
    items: List[Item] = []

    class Config:
        orm_mode = True


class UserShow(UserBase):
    id: int

    class Config:
        orm_mode = True
