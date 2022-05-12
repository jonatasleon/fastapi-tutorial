"""User services."""
from sqlalchemy.orm.session import make_transient

from app import models, schemas

from .base import Service


class EmailAlreadyRegistredError(Exception):
    """Raised when trying to create a user with an email already registred."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists.")


class UserService(Service[models.UserModel]):
    """User base service."""

    __model__ = models.UserModel

    def insert(self, model: models.UserModel) -> models.UserModel:
        """Save a user.

        :param model: the user to save
        :raises EmailAlreadyRegistredError: if the user with the given email already exists
        :return: the saved user
        """
        if self.has_email(model.email):
            raise EmailAlreadyRegistredError(model.email)
        return super().insert(model)

    def update(self, model: models.UserModel) -> models.UserModel:
        """Update a user.

        :param id_: the user id
        :param model: the user to update
        :raises NotFoundError: if the user with the given id does not exist
        :raises EmailAlreadyRegistredError: if the user with the given email already exists
        :return: the updated user
        """
        self.session.expunge(model)
        make_transient(model)
        if self.has_email(model.email):
            other_id = self.get_by_email(model.email).id
            if other_id != model.id:
                raise EmailAlreadyRegistredError(model.email)
        return super().update(model)

    def get_by_email(self, email: str) -> schemas.User:
        """Get a user by email.
        :param email: the email to get the user by
        :raises NotFoundError: if the user with the given email does not exist
        :return: the user
        """
        return self.get_one_or_raise(email=email)

    def has_email(self, email: str) -> bool:
        """Check if a email exists.
        :param email: the email to check
        :return: True if the email exists, False otherwise
        """
        return self.count(email=email) > 0
