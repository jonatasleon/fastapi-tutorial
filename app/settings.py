"""Config file for the application."""
from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = "./main.db"
