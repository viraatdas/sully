"""sully test — run pytest, optionally generate test stubs."""

import ast
import textwrap
from pathlib import Path

import click

from sully import uv
from sully.config import find_pyproject


@click.command()
@click.option("--generate", is_flag=True, help="Generate test stubs for public functions.")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def test(generate: bool, extra_args: tuple[str, ...]) -> None:
    """Run pytest. Use --generate to create test stubs."""
    if generate:
        _generate_stubs()
        return

    result = uv.run_cmd(["pytest", *extra_args], check=False)
    raise SystemExit(result.returncode)


def _generate_stubs() -> None:
    """Parse src/ for public functions and write test stubs into tests/."""
    project_root = find_pyproject().parent
    src = project_root / "src"
    tests = project_root / "tests"
    tests.mkdir(exist_ok=True)

    if not src.is_dir():
        raise click.ClickException("No src/ directory found.")

    generated = 0
    for py_file in sorted(src.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue

        funcs = _public_functions(py_file)
        if not funcs:
            continue

        rel = py_file.relative_to(src).with_suffix("")
        module = ".".join(rel.parts)
        test_name = "test_" + "_".join(rel.parts) + ".py"
        test_path = tests / test_name

        if test_path.exists():
            click.echo(f"  skip {test_path.name} (exists)")
            continue

        imports = f"from {module} import {', '.join(funcs)}\n\n"
        stubs = "\n\n".join(
            textwrap.dedent(f"""\
            def test_{fn}() -> None:
                # TODO: implement test for {fn}
                assert {fn} is not None""")
            for fn in funcs
        )
        test_path.write_text(imports + stubs + "\n")
        click.echo(f"  created {test_path.name}")
        generated += 1

    click.echo(click.style(f"Generated {generated} test file(s).", fg="green"))


def _public_functions(path: Path) -> list[str]:
    """Return names of public, module-level functions in *path*."""
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return []
    return [
        node.name
        for node in ast.iter_child_nodes(tree)
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
