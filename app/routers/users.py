from fastapi import APIRouter, Depends

from .. import schemas
from ..auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserShow)
async def read_user(current_user: schemas.UserBase = Depends(get_current_user)):
    return current_user
