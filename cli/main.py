import sys

sys.path.insert(0, "./")

import typer

from cli.db import db_cli
from cli.format import format_files

app = typer.Typer()
app.add_typer(db_cli, name="db")


@app.callback()
def callback():
    """
    Awesome CLI tool.
    """


@app.command()
def format():
    """Format the code."""
    typer.echo("Formatting code...")
    format_files()
    typer.secho("Done.", fg="green", bold=True)


if __name__ == "__main__":
    app()
