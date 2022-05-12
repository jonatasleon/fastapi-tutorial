"""Test command line interface."""
import os
from tempfile import NamedTemporaryFile

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.utils import py_files


@pytest.fixture(name="runner")
def fixture_runner():
    """Fixture for CLI runner."""
    return CliRunner()


@pytest.fixture(name="valid_file")
def fixture_valid_file():
    """Fixture for valid file."""
    with NamedTemporaryFile(mode="w+", dir="/tmp", suffix=".py", delete=False) as f:
        f.writelines(
            [
                "import os",
                "\n",
                "import sys",
                "\n",
                "\n",
                "print(os.path.abspath(sys.argv[0]))",
                "\n",
            ]
        )
        f.flush()
        yield f.name


@pytest.fixture(name="need_fix_file")
def fixture_need_fix_file():
    """Fixture for invalid file."""
    with NamedTemporaryFile(mode="w+", dir="/tmp", suffix=".py") as f:
        f.writelines(["import os", "\n", "import sys"])
        f.flush()
        yield f.name


@pytest.fixture(name="invalid_format_file")
def fixture_invalid_format_file():
    """Fixture for invalid file."""
    with NamedTemporaryFile(mode="w+", dir="/tmp", suffix=".py") as f:
        f.writelines(["imp;ort os", "\n", "import not_existing_module"])
        f.flush()
        yield f.name


@pytest.fixture(name="invalid_imports_file")
def fixture_invalid_imports_file():
    """Fixture for invalid file."""
    with NamedTemporaryFile(mode="w+", dir="/tmp", suffix=".py", delete=False) as f:
        f.writelines(["import not_existing_module", "\n"])
        f.flush()
        yield f.name


def test_cli_help(runner: CliRunner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Awesome CLI tool." in result.output


def test_cli_format_works_with_valid_file(runner: CliRunner, valid_file):
    result = runner.invoke(app, ["source", "format", valid_file])
    assert "Formatting code... done." in result.output, "Unexpected message"
    assert "Formatting imports... done." in result.output, "Unexpected message"
    assert result.exit_code == 0, "Expected 0 exit code"


def test_cli_verbose_works(runner: CliRunner, valid_file):
    result = runner.invoke(app, ["source", "--verbose", "format", valid_file])
    assert "All done!" in result.output
    assert result.exit_code == 0


def test_cli_format_works_with_need_fix_file(runner: CliRunner, need_fix_file):
    result = runner.invoke(app, ["source", "format", need_fix_file])
    assert "Formatting code... done." in result.output, "Unexpected message"
    assert "Formatting imports... done." in result.output, "Unexpected message"
    assert result.exit_code == 0, "Expected 0 exit code"


def test_cli_format_exits_1_with_invalid_format_file(runner: CliRunner, invalid_format_file):
    result = runner.invoke(app, ["source", "format", invalid_format_file])
    assert "Formatting code... error." in result.output, "Unexpected message"
    assert result.exit_code == 1, "Expected 0 exit code"


def test_cli_check_works_with_valid_file(runner: CliRunner, valid_file):
    result = runner.invoke(app, ["source", "check", valid_file])
    assert "Checking code... done." in result.output
    assert result.exit_code == 0


def test_exit_1_when_file_does_not_exist(runner: CliRunner):
    result = runner.invoke(app, ["source", "check", "not_existing_file"])
    assert result.output == "File(s) not found: not_existing_file\n"
    assert result.exit_code == 1


def test_cli_check_fails_with_invalid_imports_file(runner: CliRunner, invalid_format_file):
    result = runner.invoke(app, ["source", "check", invalid_format_file])
    assert "Checking code... error." in result.output
    assert result.exit_code == 1


def test_lint_works_with_valid_file(runner: CliRunner, valid_file):
    result = runner.invoke(app, ["source", "lint", valid_file])
    assert "Linting code... done." in result.output
    assert result.exit_code == 0


def test_validate_files_returns_python_files_under_version_control(
    monkeypatch: pytest.MonkeyPatch, runner: CliRunner, valid_file
):
    monkeypatch.setattr(__import__("cli.source", fromlist=[None]), "py_files", lambda: [valid_file])
    result = runner.invoke(app, ["source", "--verbose", "check"])
    assert result.exit_code == 0
    assert f"Files: {valid_file}" in result.output
    assert "Checking code... done." in result.output


def test_cli_db_create_works(runner: CliRunner):
    with NamedTemporaryFile(mode="wb+", dir="/tmp", suffix=".db") as f:
        runner.env["DATABASE_URL"] = f.name
        result = runner.invoke(app, ["db", "create"])
        assert result.exit_code == 0


def test_cli_db_create_fails_with_invalid_db_url(runner: CliRunner):
    runner.env["DATABASE_URL"] = "///:invalid:///"
    result = runner.invoke(app, ["db", "create"])
    assert result.exit_code == 1


def test_cli_db_drop_works(runner: CliRunner):
    with NamedTemporaryFile(mode="wb+", dir="/tmp", suffix=".db") as f:
        runner.env["DATABASE_URL"] = f.name
        runner.invoke(app, ["db", "create"])
        result = runner.invoke(app, ["db", "drop"])
        assert result.exit_code == 0


def test_cli_db_drop_fails_when_db_does_not_exist(runner: CliRunner):
    runner.env["DATABASE_URL"] = "non_existing_file.db"
    result = runner.invoke(app, ["db", "drop"])
    assert result.exit_code == 1


def test_cli_db_shell_works(monkeypatch: pytest.MonkeyPatch, runner: CliRunner):
    def mock_embed(**kwargs):
        assert "user_ns" in kwargs, "Embed shell was not called with user_ns"
        assert "header" in kwargs, "Embed shell was not called with header"
        context = kwargs["user_ns"]
        message_header = kwargs["header"]
        assert "session" in context, "Session was not provided to embed shell"
        assert "services" in context, "Services were not provided to embed shell"
        assert "models" in context, "Models were not provided to embed shell"
        assert message_header == "Context: models, services, session\n", "Unexpected message header"
        return None

    monkeypatch.setattr(__import__("IPython"), "embed", mock_embed)

    with NamedTemporaryFile(mode="wb+", dir="/tmp", suffix=".db") as f:
        runner.env["DATABASE_URL"] = f.name
        result = runner.invoke(app, ["db", "shell"])
        assert result.exit_code == 0, "Expected 0 exit code"


def test_cli_db_shell_fails_when_db_does_not_exist(runner: CliRunner):
    runner.env["DATABASE_URL"] = "non_existing_file.db"
    result = runner.invoke(app, ["db", "shell"])
    assert (
        result.output
        == "Failed to open shell: non_existing_file.db does not exist or is not a file\n"
    )
    assert result.exit_code == 1, "Expected 1 exit code"


def test_py_files_must_return_a_list_of_files():
    files = py_files()
    assert isinstance(files, list), "py_files must return a list"
    assert all(isinstance(f, str) for f in files), "py_files must return a list of strings"
    assert len(files) > 0, "py_files must return a list with at least one file"
    assert all(os.path.isfile(f) for f in files), "py_files must return a list of existing files"
    assert all(f.endswith(".py") for f in files), "py_files must return a list of python files"
