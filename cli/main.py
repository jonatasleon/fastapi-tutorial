import typer

from cli.db import db_cli
from cli.source import source_cli

app = typer.Typer()
app.add_typer(db_cli, name="db")
app.add_typer(source_cli, name="source")


@app.callback()
def callback():
    """
    Awesome CLI tool.
    """
