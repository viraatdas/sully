"""sully doc — generate documentation via pdoc."""

import click

from sully import uv
from sully.config import get_doc_config


def run_pdoc(output: str) -> int:
    """Run pdoc and return the exit code."""
    result = uv.run_cmd(["pdoc", f"--output-directory={output}", "src/"], check=False)
    return result.returncode


@click.command()
def doc() -> None:
    """Generate HTML docs from docstrings via pdoc."""
    cfg = get_doc_config()
    output = cfg["output"]

    rc = run_pdoc(output)
    if rc != 0:
        raise click.ClickException("pdoc failed.")
    click.echo(click.style(f"Docs written to {output}/", fg="green"))
