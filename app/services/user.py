"""User services."""
from app import models, schemas

from .base import Service


class EmailAlreadyRegistredError(Exception):
    """Raised when trying to create a user with an email already registred."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists.")


class UserService(Service[models.User]):
    """User base service."""

    __model__ = models.User

    def get_by_email(self, email: str) -> schemas.User:
        """Get a user by email.
        :param email: the email to get the user by
        :raises NotFoundError: if the user with the given email does not exist
        :return: the user
        """
        return self.get_one_or_raise(email=email)

    def has_user(self, email: str) -> bool:
        """Check if a user exists.
        :param email: the email to check
        :return: True if the user exists, False otherwise
        """
        return self.count(email=email) > 0
