from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import get_current_user
from ..database import get_db
from ..services import NotFoundError
from ..services import ScopedItemService as ItemService

router = APIRouter(prefix="/items", tags=["items"])


def get_service(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get :class:`ItemService` service for the current user."""
    return ItemService(db, current_user)


@router.get("", response_model=List[schemas.Item])
async def read_items(service: ItemService = Depends(get_service)):
    return service.get_all()


@router.post("", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: schemas.ItemCreate,
    service: ItemService = Depends(get_service),
):
    return service.save(item)


@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int,
    item: schemas.ItemUpdate,
    service: ItemService = Depends(get_service),
):
    try:
        return service.update(item_id, item)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(
    item_id: int,
    service: ItemService = Depends(get_service),
):
    try:
        return service.get_one(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        )


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
    try:
        service.delete(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        )
