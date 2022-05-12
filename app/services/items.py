"""Item services."""
from sqlalchemy.orm import Session

from .. import models
from .base import Service


class ItemService(Service[models.ItemModel]):
    """Item Service that inherits from :class:`Service` abstract class.
    This class is responsible for CRUD operations on :class:`app.models.Item`."""

    __model__ = models.ItemModel


class OwnedItemService(ItemService):
    """Scoped Item Service that inherits from :class:`app.services.ItemService`
    abstract class. It apply a scope to the items that can be
    retrieved or created by the current user.

    :param session: the database session
    :param owner: the owner of the items"""

    def __init__(self, session: Session, owner: models.UserModel):
        """Initialize the service."""
        super().__init__(session)
        self.owner = owner
        self.update_default_params(owner_id=owner.id)
