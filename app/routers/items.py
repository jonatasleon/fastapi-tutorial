"""Items router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import get_current_user
from ..database import get_db
from ..services import NotFoundError
from ..services import OwnedItemService as ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_service(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get :class:`OwnedItemService` service for the current user."""
    return ItemService(db, current_user)


@router.get("", response_model=List[schemas.Item])
async def read_items(service: ItemService = Depends(get_service)):
    """Get all items."""
    return service.get_all()


@router.post("", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: schemas.ItemCreate,
    service: ItemService = Depends(get_service),
):
    """Create an item."""
    return service.save(item)


@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    service: ItemService = Depends(get_service),
):
    """Update an item."""
    try:
        return service.update(item_id, item)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(
    item_id: int,
    service: ItemService = Depends(get_service),
):
    """Get an item by id."""
    try:
        return service.get_one(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        ) from e


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.Detail},
    },
)
async def delete_item(
    item_id: int,
    service: ItemService = Depends(get_service),
):
    """Delete an item by id."""
    try:
        service.delete(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        ) from e
