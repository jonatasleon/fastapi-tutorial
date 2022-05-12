import subprocess
import sys
from functools import lru_cache


@lru_cache
def py_files():
    """Return a list of all Python files under version control."""
    GIT_LS_FILES_CMD = ["git", "ls-files", "*.py"]
    return (
        subprocess.run(GIT_LS_FILES_CMD, stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")[:-1]
    )


def format_files(files, check=False):
    CMD = [sys.executable, "-m", "black"]
    if check:
        CMD.extend(["--check", "--diff"])
    CMD.extend(files)
    return subprocess.run(CMD, capture_output=True)


def format_imports(files, check=False):
    CMD = [sys.executable, "-m", "isort", "-v"]
    if check:
        CMD.append("--check-only")
    CMD.extend(files)
    return subprocess.run(CMD, capture_output=True)


def lint_files(files):
    return (
        subprocess.run(
            [
                sys.executable,
                "-m",
                "flake8",
                "--count",
                "--select=E9,F63,F7,F82",
                "--show-source",
                "--statistics",
            ]
            + files,
            capture_output=True,
        ),
        subprocess.run(
            [
                sys.executable,
                "-m",
                "flake8",
                "--count",
                "--exit-zero",
                "--max-complexity=10",
                "--max-line-length=100",
                "--statistics",
            ]
            + files,
            capture_output=True,
        ),
    )
