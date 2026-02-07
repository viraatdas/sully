"""Wrapper around uv subprocess calls."""

import shutil
import subprocess
import sys
from pathlib import Path


def ensure_uv() -> str:
    """Return the path to uv, or exit with a clear error."""
    uv = shutil.which("uv")
    if uv is None:
        sys.exit(
            "Error: uv is not installed.\n"
            "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "Or see: https://docs.astral.sh/uv/getting-started/installation/"
        )
    return uv


def _run(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a uv command, forwarding stdout/stderr to the terminal."""
    uv = ensure_uv()
    return subprocess.run(
        [uv, *args],
        cwd=cwd,
        check=check,
    )


def add(packages: list[str], *, dev: bool = False, group: str | None = None, cwd: Path | None = None) -> None:
    """Add dependencies via `uv add`."""
    args = ["add"]
    if dev:
        args.append("--dev")
    elif group:
        args.extend(["--group", group])
    args.extend(packages)
    _run(args, cwd=cwd)


def remove(packages: list[str], *, cwd: Path | None = None) -> None:
    """Remove dependencies via `uv remove`."""
    _run(["remove", *packages], cwd=cwd)


def sync(*, cwd: Path | None = None) -> None:
    """Install all dependencies via `uv sync`."""
    _run(["sync"], cwd=cwd)


def run_script(script: str, *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a Python script via `uv run python <script>`."""
    return _run(["run", "python", script], cwd=cwd, check=False)


def run_cmd(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run an arbitrary command via `uv run <args>`."""
    return _run(["run", *args], cwd=cwd, check=check)


def pin_python(version: str, *, cwd: Path | None = None) -> None:
    """Pin the Python version via `uv python pin`."""
    _run(["python", "pin", version], cwd=cwd)


def python_install(version: str, *, cwd: Path | None = None) -> None:
    """Install a Python version via `uv python install`."""
    _run(["python", "install", version], cwd=cwd)
