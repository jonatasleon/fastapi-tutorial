"""Items router."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import get_current_user, get_owned_item_service, get_session
from app.services import NotFoundError
from app.services import OwnedItemService as ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=List[schemas.Item])
async def read_items(
    db: Session = Depends(get_session), owner: schemas.User = Depends(get_current_user)
):
    """Get all items."""
    service = ItemService(db, owner)
    return service.get_all()


@router.post("", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: schemas.ItemCreate, service: ItemService = Depends(get_owned_item_service)
):
    """Create an item."""
    return service.save(item)


@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int, item: schemas.ItemUpdate, service: ItemService = Depends(get_owned_item_service)
):
    """Update an item."""
    try:
        return service.update(item_id, item)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, service: ItemService = Depends(get_owned_item_service)):
    """Get an item by id."""
    try:
        return service.get_by_id(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        ) from e


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": schemas.Detail}},
)
async def delete_item(item_id: int, service: ItemService = Depends(get_owned_item_service)):
    """Delete an item by id."""
    try:
        service.delete(item_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {e.id} not found",
        ) from e
