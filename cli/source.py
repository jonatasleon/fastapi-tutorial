from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Optional

import typer

from cli.utils import format_files, format_imports, lint_files, py_files

source_cli = typer.Typer()
state = {"verbose": False}


@source_cli.callback()
def callback(verbose: bool = False):
    """Callback for CLI."""
    state["verbose"] = verbose


def validate_files(files: Optional[List[Path]]) -> List[Path]:
    """Validate if files exist."""
    if not files:
        return py_files()

    not_found = [f.name for f in files if not f.exists()]
    if not_found:
        typer.echo(f"File(s) not found: {', '.join(not_found)}", err=True)
        raise typer.Exit(1)

    return files


@source_cli.command()
def format(
    files: List[Path] = typer.Argument(
        default=None,
        callback=validate_files,
        show_default=False,
        help="Files to format (default: all Python files under version control)",
    )
):
    """Format the code."""

    def handle_result(result, verbose, output_key="stdout", error_key="stderr"):
        """Handle result."""
        if result.returncode == 0:
            typer.secho(" done.", fg="green")
            if verbose:
                typer.echo(getattr(result, output_key).decode("utf-8"), nl=False)
        else:
            typer.secho(" error.", fg="red")
            typer.echo(getattr(result, error_key).decode("utf-8"), err=True, nl=False)
            return typer.Exit(1)
        return None

    exceptions = []
    typer.echo("Formatting imports...", nl=False)
    result = format_imports(files)
    exceptions.append(handle_result(result, state["verbose"]))

    typer.echo("Formatting code...", nl=False)
    result = format_files(files)
    exceptions.append(handle_result(result, state["verbose"], output_key="stderr"))

    if any([e is not None for e in exceptions]):
        raise Exception(exceptions)


@source_cli.command()
def check(
    files: List[Path] = typer.Argument(
        default=None,
        callback=validate_files,
        show_default=False,
        help="Files to check (default: all Python files under version control)",
    )
):
    """Check the code"""
    kwargs = {"check": True, "files": files}
    if state["verbose"]:
        typer.echo(f"Files: {', '.join([str(f) for f in files])}")
    typer.echo("Checking code...", nl=False)
    results = ThreadPool().map(lambda fn: fn(**kwargs), [format_imports, format_files])
    if any([p.returncode for p in results]):
        typer.secho(" error.", fg="red")
        for p in results:
            if p.returncode:
                typer.echo(p.stderr.decode(), err=True)
        raise typer.Exit(1)
    typer.secho(" done.", fg="green")


@source_cli.command()
def lint(
    files: List[Path] = typer.Argument(
        default=None,
        callback=validate_files,
        show_default=False,
        help="Files to lint (default: all Python files under version control)",
    )
):
    """Lint the code."""
    typer.echo("Linting code...", nl=False)
    lint_1, lint_2 = lint_files(files)
    typer.secho(" done.", fg="green", bold=True)
    typer.echo(lint_1.stdout.decode(), nl=False)
    typer.echo(lint_1.stderr.decode(), err=True, nl=False)
    typer.echo(lint_2.stdout.decode(), nl=False)
    typer.echo(lint_1.stderr.decode(), err=True, nl=False)
