"""Test command line interface."""
from tempfile import NamedTemporaryFile

import pytest
from typer.testing import CliRunner

from cli.main import app
from cli.source import validate_files


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


def test_validate_files_returns_python_files_under_version_control():
    files = validate_files(None)
    assert len(files) > 0
    assert all(file.endswith(".py") for file in files)


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
