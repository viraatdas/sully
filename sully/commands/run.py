"""sully run — type-check gate + run main script."""

import sys

import click

from sully import uv
from sully.config import get_check_config, get_main_script


@click.command()
@click.option("--no-check", is_flag=True, help="Skip the type-check gate.")
def run(no_check: bool) -> None:
    """Type-check then run the project's main script."""
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

    # Find main script
    main_script = get_main_script()
    if not main_script:
        raise click.ClickException(
            "No main script configured. Set [tool.sully] main = 'src/…/main.py' in pyproject.toml."
        )

    click.echo(f"Running {main_script}...")
    result = uv.run_script(main_script)
    sys.exit(result.returncode)
