"""Database module."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import Settings

settings = Settings()

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
