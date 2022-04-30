from fastapi import Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app import schemas
from app.services import UserService
from app.auth import Auth, get_current_user as get_current_user_, oauth2_scheme
from app.services.items import ItemService, OwnedItemService


def get_user_service(db: Session = Depends(get_db)):
    """Wrapper creates a new instance of UserService."""
    return UserService(db)


def get_item_service(db: Session = Depends(get_db)):
    """Wrapper creates a new instance of ItemService."""
    return ItemService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> schemas.User:
    """Wrapper for app.auth.get_current_user()"""
    return get_current_user_(token, user_service)


def get_owned_item_service(db: Session = Depends(get_db), owner: schemas.User = Depends(get_current_user)):
    """Wrapper creates a new instance of OwnedItemService."""
    return OwnedItemService(db, owner)


def get_auth(
    user_service: UserService = Depends(get_user_service),
):
    """Wrapper for app.auth.Auth"""
    return Auth(user_service)
