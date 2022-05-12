from functools import lru_cache
from typing import Generator

from sqlalchemy.orm import Session

from app.config import Settings
from app.database import engine


@lru_cache
def get_settings():
    return Settings()


def get_session(engine=engine) -> Generator[Session, None, None]:
    """Instantiate and return a new Session object.
    Works as a context manager.

    :return: a new Session object
    """
    session = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield session
    finally:
        session.close()
