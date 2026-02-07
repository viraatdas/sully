"""sully remove — remove a dependency."""

import click

from sully import uv


@click.command()
@click.argument("packages", nargs=-1, required=True)
def remove(packages: tuple[str, ...]) -> None:
    """Remove one or more dependencies via uv."""
    uv.remove(list(packages))
