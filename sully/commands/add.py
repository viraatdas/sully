"""sully add — add a dependency."""

import click

from sully import uv


@click.command()
@click.argument("packages", nargs=-1, required=True)
@click.option("--dev", is_flag=True, help="Add as a dev dependency.")
@click.option("--group", default=None, help="Add to a named dependency group.")
def add(packages: tuple[str, ...], dev: bool, group: str | None) -> None:
    """Add one or more dependencies via uv."""
    uv.add(list(packages), dev=dev, group=group)
