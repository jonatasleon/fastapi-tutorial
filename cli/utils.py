import subprocess
import sys


def format_files():
    GIT_LS_FILES_CMD = ["git", "ls-files", "*.py"]
    py_files = (
        subprocess.run(GIT_LS_FILES_CMD, stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")[:-1]
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "black",
        ]
        + py_files,
    )
    subprocess.run([sys.executable, "-m", "isort"] + py_files)


def lint_files():
    GIT_LS_FILES_CMD = ["git", "ls-files", "*.py"]
    py_files = (
        subprocess.run(GIT_LS_FILES_CMD, stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .split("\n")[:-1]
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "flake8",]+ py_files,
        )
