"""sully check — run pyright type checker (core feature)."""

import sys

import click

from sully import uv
from sully.config import get_check_config


@click.command()
def check() -> None:
    """Run pyright type checking against the project source."""
    cfg = get_check_config()
    mode = cfg["mode"]

    if mode == "off":
        click.echo("Type checking is disabled (mode = 'off').")
        return

    result = uv.run_cmd(["pyright", f"--level={mode}"], check=False)
    if result.returncode != 0:
        click.echo(click.style("Type errors found.", fg="red", bold=True))
        sys.exit(result.returncode)
    else:
        click.echo(click.style("All clear — no type errors.", fg="green", bold=True))
