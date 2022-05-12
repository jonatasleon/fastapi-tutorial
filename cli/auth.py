import typer
from sqlalchemy import create_engine

from app.auth import Auth
from app.dependencies import get_session
from app.services import UserService
from cli.commons import DEFAULT_DATABASE_URL

auth_cli = typer.Typer()


@auth_cli.callback()
def callback():
    """Callback for CLI."""


@auth_cli.command()
def add_user(
    email: str,
    pwd: str = typer.Option(..., prompt=True, hide_input=True),
    db_path: str = typer.Option(DEFAULT_DATABASE_URL, envvar="DATABASE_URL"),
):
    """Add user."""
    engine = create_engine(url=f"sqlite:///{db_path}", echo=True)
    with get_session(engine) as session:
        auth = Auth(UserService(session))
        auth.create_user(name=email.split("@")[0], email=email, password=pwd)
