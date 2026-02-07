"""sully doc — generate documentation via pdoc."""

import click

from sully import uv
from sully.config import load


@click.command()
def doc() -> None:
    """Generate HTML docs from docstrings via pdoc."""
    cfg = load()
    output = cfg.get("doc", {}).get("output", "docs")

    result = uv.run_cmd(
        ["pdoc", f"--output-directory={output}", "src/"],
        check=False,
    )
    if result.returncode != 0:
        raise click.ClickException("pdoc failed.")
    click.echo(click.style(f"Docs written to {output}/", fg="green"))
