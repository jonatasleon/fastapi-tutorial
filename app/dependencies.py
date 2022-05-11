from functools import lru_cache
from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.settings import Settings


@lru_cache
def get_settings():
    return Settings()


def get_db() -> Generator[Session, None, None]:
    """Instantiate and return a new Session object.
    Works as a context manager.

    :return: a new Session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
