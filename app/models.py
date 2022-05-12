# pylint: disable=too-few-public-methods
"""Models."""
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

_Base = declarative_base()


class Base(_Base):
    """Base model for all models."""

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)


class UserModel(Base):
    """User model."""

    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("ItemModel", back_populates="owner")


class ItemModel(Base):
    """Item model."""

    __tablename__ = "items"

    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    is_offer = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("UserModel", back_populates="items")
