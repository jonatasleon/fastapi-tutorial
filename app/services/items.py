"""Item services."""
from sqlalchemy.orm import Session

from .. import models
from .base import Service


class ItemService(Service[models.Item]):
    """Item Service that inherits from :class:`Service` abstract class.
    This class is responsible for CRUD operations on :class:`app.models.Item`."""

    __model__ = models.Item


class OwnedItemService(ItemService):
    """Scoped Item Service that inherits from :class:`app.services.ItemService`
    abstract class. It apply a scope to the items that can be
    retrieved or created by the current user.

    :param db: the database session
    :param owner: the owner of the items"""

    def __init__(self, db: Session, owner: models.User):
        """Initialize the service."""
        super().__init__(db)
        self.owner = owner
        self.update_default_params(owner_id=owner.id)
