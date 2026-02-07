"""sully sync — install all project dependencies."""

import click

from sully import uv


@click.command()
def sync() -> None:
    """Install all dependencies via uv sync."""
    uv.sync()
    click.echo(click.style("Dependencies synced.", fg="green"))
