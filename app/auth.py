"""Authentication module"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext

from app.schemas import Token, TokenData, User, UserCreate
from app.services import EmailAlreadyRegistredError, NotFoundError, UserService

SECRET_KEY = "d97c3cdfff3479ed1587a4143ad5b925ae4109fd59a7a74cddb505489b35102f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


class CredentialsException(HTTPException):
    """Credentials Exception.
    Exception for when an incorrect email or password is given.
    :param status_code: HTTP status code
    :param detail: Error message
    :param headers: Optional headers to add to the response
    """

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Incorrect email or password",
        headers: Optional[dict] = None,
    ):
        if headers is None:
            headers = {}
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def get_current_user(token: str, service: UserService):
    """Get the current user given an access token."""
    try:
        token_data = decode_access_token(token)
    except InvalidTokenError as e:
        raise CredentialsException(
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    try:
        user = service.get_by_email(token_data.email)
    except NotFoundError as e:
        raise CredentialsException(
            detail="Could not find user by email",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return user


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> Token:
    """Create an access token for a user.

    :param user: the user to create the token for
    :param expires_delta: optional minutes time delta for token expiration
    :return: a :class:`Token` object
    """
    to_encode: Dict[str, Any] = {"sub": user.email}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


def decode_access_token(token: str) -> TokenData:
    """Decode an access token and return a TokenData object.
    :param token: a string of the access token
    :return: a :class:`TokenData` object
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    try:
        email: str = payload["sub"]
    except KeyError as e:
        raise InvalidTokenError(token) from e
    return TokenData(email=email)


class InvalidTokenError(Exception):
    """Raised when an invalid token is supplied.
    :param token: the token that was supplied."""

    def __init__(self, token: str):
        self.token = token
        super().__init__(f"Invalid token: {token}")


class Auth:
    """Authentication class.
    :param service: UserService
    """

    def __init__(self, service: UserService):
        self.service: UserService = service
        self.pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _verify_password(self, password, hashed) -> bool:
        """Verify a plain text password against a hashed one.
        :param password: plain text password
        :param hashed: hashed password
        :return: True if passwords match, False otherwise
        """
        return self.pwd_ctx.verify(password, hashed)

    def _get_password_hash(self, password) -> str:
        """Hash a password using the bcrypt algorithm.
        :param password: plain text password
        :return: hashed password
        """
        return self.pwd_ctx.hash(password)

    def create_user(self, name: str, email: str, password: str) -> User:
        """Create a new user.
        :param user: the user to create.
        :return: the created user.
        """
        if self.service.has_email(email):
            raise EmailAlreadyRegistredError(email)

        password = self._get_password_hash(password)
        return self.service.save(
            self.service.create_model(name=name, email=email, password=password)
        )

    def authenticate(self, form_data: OAuth2PasswordRequestForm) -> Union[User, None]:
        """Authenticate a user.
        :param form_data: the form data
        :return: the user if authenticated, False otherwise
        """
        try:
            user = self.service.get_by_email(form_data.username)
        except NotFoundError:
            return False

        if not self._verify_password(form_data.password, user.password):
            return False
        return user
