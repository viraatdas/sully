"""sully run — type-check gate + doc gate + run main script."""

import sys

import click

from sully import uv
from sully.commands.doc import run_pdoc
from sully.config import get_check_config, get_doc_config, get_main_script


@click.command()
@click.option("--no-check", is_flag=True, help="Skip the type-check gate.")
@click.option("--no-doc", is_flag=True, help="Skip the doc-generation gate.")
def run(no_check: bool, no_doc: bool) -> None:
    """Type-check, generate docs, then run the project's main script."""
    cfg = get_check_config()

    # Type-check gate
    if not no_check and cfg["check-before-run"] and cfg["mode"] != "off":
        click.echo("Running type check...")
        result = uv.run_cmd(["pyright", f"--level={cfg['mode']}"], check=False)
        if result.returncode != 0:
            click.echo(click.style("Type errors found — fix before running.", fg="red", bold=True))
            click.echo("Use --no-check to bypass.")
            sys.exit(result.returncode)
        click.echo(click.style("Type check passed.", fg="green"))

    # Doc-generation gate
    doc_cfg = get_doc_config()
    if not no_doc and doc_cfg["doc-before-run"]:
        click.echo("Generating docs...")
        rc = run_pdoc(doc_cfg["output"])
        if rc != 0:
            click.echo(click.style("Doc generation failed — fix before running.", fg="red", bold=True))
            click.echo("Use --no-doc to bypass.")
            sys.exit(rc)
        click.echo(click.style("Docs generated.", fg="green"))

    # Find main script
    main_script = get_main_script()
    if not main_script:
        raise click.ClickException(
            "No main script configured. Set [tool.sully] main = 'src/…/main.py' in pyproject.toml."
        )

    click.echo(f"Running {main_script}...")
    result = uv.run_script(main_script)
    sys.exit(result.returncode)
