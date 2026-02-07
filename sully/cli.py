"""Click CLI group for sully."""

import click

from sully import __version__
from sully.commands import init, add, remove, sync, check, run, test, doc


@click.group()
@click.version_option(__version__, prog_name="sully")
def cli() -> None:
    """sully — Production-ready Python, from the first line."""


cli.add_command(init.init)
cli.add_command(add.add)
cli.add_command(remove.remove)
cli.add_command(sync.sync)
cli.add_command(check.check)
cli.add_command(run.run)
cli.add_command(test.test)
cli.add_command(doc.doc)
