from functools import lru_cache
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app import schemas
from app.auth import Auth
from app.auth import get_current_user as get_current_user_
from app.auth import oauth2_scheme
from app.config import Settings
from app.database import engine
from app.services import UserService
from app.services.items import ItemService, OwnedItemService


@lru_cache
def get_settings():
    return Settings()


def get_session() -> Generator[Session, None, None]:
    """Instantiate and return a new Session object.
    Works as a context manager.

    :return: a new Session object
    """
    session = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield session
    finally:
        session.close()


def get_user_service(db: Session = Depends(get_session)):
    """Wrapper creates a new instance of UserService."""
    return UserService(db)


def get_item_service(db: Session = Depends(get_session)):
    """Wrapper creates a new instance of ItemService."""
    return ItemService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> schemas.User:
    """Wrapper for app.auth.get_current_user()"""
    return get_current_user_(token, user_service)


def get_owned_item_service(
    db: Session = Depends(get_session), owner: schemas.User = Depends(get_current_user)
):
    """Wrapper creates a new instance of OwnedItemService."""
    return OwnedItemService(db, owner)


def get_auth(
    user_service: UserService = Depends(get_user_service),
):
    """Wrapper for app.auth.Auth"""
    return Auth(user_service)
