import os

import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import IPython

from app.models import Base
from cli.commons import DEFAULT_DATABASE_URL

db_cli = typer.Typer()


@db_cli.callback()
def callback():
    """DB commands."""


@db_cli.command()
def shell(path: str = DEFAULT_DATABASE_URL):
    """Open a shell with the database session."""
    try:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{path} does not exist or is not a file")
        _engine = create_engine(
            f"sqlite:///{os.path.abspath(path)}",
            connect_args={"check_same_thread": False},
        )
        _session = Session(bind=_engine)
    except Exception as e:
        typer.echo(f"Failed to open shell: {e}", err=True)
        raise typer.Exit(1) from e

    with _session as session:
        try:
            context = {
                "session": session,
                "services": __import__("app.services", fromlist=["services"]),
                "models": __import__("app.models", fromlist=["models"]),
            }
            available_objects = ", ".join(sorted([o for o in context]))
            message_header = f"Context: {available_objects}\n"
            IPython.embed(colors="neutral", header=message_header, user_ns=context)
        finally:
            session.close()


@db_cli.command()
def create(path: str = DEFAULT_DATABASE_URL):
    """Create the database.
    :param path: the path to the database
    """
    typer.echo(f"Creating database {path}...", nl=False)
    try:
        engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(engine)
    except Exception as e:
        typer.secho(" error.", fg="red")
        typer.echo(f"Failed to create database: {e}", err=True)
        raise typer.Exit(1) from e
    typer.secho(" done.", fg="green")


@db_cli.command()
def drop(path: str = DEFAULT_DATABASE_URL):
    """Drop database

    :param path: the path to the database, defaults to sql_app.db
    """
    typer.echo(f"Dropping database {path}...", nl=False)
    try:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{path} does not exist or is not a file")
        engine = create_engine(f"sqlite:///{path}")
        Base.metadata.drop_all(engine)
    except Exception as e:
        typer.secho(" error.", fg="red")
        typer.echo(f"Failed to drop database: {e}", err=True)
        raise typer.Exit(1) from e
    typer.secho(" done.", fg="green")
