"""Basic tests for the sully CLI."""

from click.testing import CliRunner

from sully.cli import cli


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "sully" in result.output


def test_cli_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.output


def test_init_requires_name() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code != 0


def test_add_requires_package() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["add"])
    assert result.exit_code != 0


def test_remove_requires_package() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["remove"])
    assert result.exit_code != 0


def test_all_commands_registered() -> None:
    """Every planned command should be present in the CLI group."""
    expected = {"init", "add", "remove", "sync", "check", "run", "test", "doc"}
    actual = set(cli.commands.keys())
    assert expected == actual


def test_each_command_has_help() -> None:
    """Every command should respond to --help without crashing."""
    runner = CliRunner()
    for name in cli.commands:
        result = runner.invoke(cli, [name, "--help"])
        assert result.exit_code == 0, f"{name} --help failed: {result.output}"


def test_unknown_command() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["does-not-exist"])
    assert result.exit_code != 0
    assert "No such command" in result.output
