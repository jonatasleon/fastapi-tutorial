from typing import Optional

from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    is_offer: bool = False


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    is_offer: Optional[bool] = None


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
