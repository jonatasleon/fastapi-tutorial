from unittest.mock import DEFAULT

from app.settings import Settings

settings = Settings()
DEFAULT_DATABASE_URL = settings.database_url
