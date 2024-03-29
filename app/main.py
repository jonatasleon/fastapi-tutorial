"""Main module."""
from fastapi import FastAPI

from app.routers import auth_router, items_router, users_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(items_router)
app.include_router(users_router)
