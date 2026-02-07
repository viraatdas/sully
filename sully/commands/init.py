"""sully init — scaffold a new typed Python project."""

import json
from pathlib import Path

import click

from sully import uv


@click.command()
@click.argument("name")
@click.option("--python", "python_version", default="3.12", help="Python version to pin.")
def init(name: str, python_version: str) -> None:
    """Create a new typed Python project."""
    root = Path.cwd() / name

    if root.exists():
        raise click.ClickException(f"Directory '{name}' already exists.")

    pkg = name.replace("-", "_")

    # -- directory skeleton --------------------------------------------------
    (root / "src" / pkg).mkdir(parents=True)
    (root / "tests").mkdir()

    # -- pyproject.toml ------------------------------------------------------
    (root / "pyproject.toml").write_text(
        f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "A sully project — typed, tested, documented."
requires-python = ">={python_version}"
dependencies = []

[dependency-groups]
dev = ["pyright", "pytest", "pdoc"]

[tool.sully]
main = "src/{pkg}/main.py"

[tool.sully.check]
mode = "strict"
check-before-run = true

[tool.sully.doc]
output = "docs"
"""
    )

    # -- pyrightconfig.json --------------------------------------------------
    (root / "pyrightconfig.json").write_text(
        json.dumps(
            {
                "include": ["src"],
                "typeCheckingMode": "strict",
                "pythonVersion": python_version,
            },
            indent=2,
        )
        + "\n"
    )

    # -- source files --------------------------------------------------------
    (root / "src" / pkg / "__init__.py").write_text(
        f'"""Top-level package for {name}."""\n'
    )

    (root / "src" / pkg / "main.py").write_text(
        f'''\
"""{name} — entry point."""


def greet(name: str = "world") -> str:
    """Return a greeting string."""
    return f"Hello, {{name}}!"


def main() -> None:
    """Run the application."""
    print(greet())


if __name__ == "__main__":
    main()
'''
    )

    (root / "src" / pkg / "py.typed").write_text("")

    # -- tests ---------------------------------------------------------------
    (root / "tests" / "test_main.py").write_text(
        f"""\
from {pkg}.main import greet


def test_greet_default() -> None:
    assert greet() == "Hello, world!"


def test_greet_name() -> None:
    assert greet("sully") == "Hello, sully!"
"""
    )

    # -- .gitignore ----------------------------------------------------------
    (root / ".gitignore").write_text(
        """\
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
docs/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.DS_Store
"""
    )

    # -- README --------------------------------------------------------------
    (root / "README.md").write_text(f"# {name}\n\nA sully project — typed, tested, documented from the start.\n")

    # -- uv setup ------------------------------------------------------------
    uv.ensure_uv()
    uv.pin_python(python_version, cwd=root)
    uv.sync(cwd=root)

    click.echo(click.style(f"Created project '{name}'.", fg="green", bold=True))
    click.echo(f"  cd {name} && sully check")
