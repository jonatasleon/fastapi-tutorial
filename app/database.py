"""Database module."""
from sqlalchemy import create_engine

from app.config import Settings

settings = Settings()

DATABASE_URL = settings.database_url

engine = create_engine(
    f"sqlite:///{DATABASE_URL}",
    connect_args={"check_same_thread": False},
)
