"""Authencation router."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import Auth, CredentialsException, create_access_token
from app.dependencies import get_auth
from app.schemas import Token, User, UserCreate, UserShow
from app.services import EmailAlreadyRegistredError

router = APIRouter(tags=["auth"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def create_user(user: UserCreate, auth: Auth = Depends(get_auth)):
    """Create a new user."""
    try:
        return auth.create_user(**user.dict())
    except EmailAlreadyRegistredError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User email {e.email} already used",
        ) from e


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth: Auth = Depends(get_auth),
):
    """Authenticate a user and return a token."""
    if not (user := auth.authenticate(form_data)):
        raise CredentialsException(
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_access_token(user)
