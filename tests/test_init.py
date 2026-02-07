"""Tests for sully init — project scaffolding."""

import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from sully.cli import cli


def _invoke_init(tmp_path: Path, name: str = "myapp", extra_args: list[str] | None = None) -> object:
    """Helper: run `sully init` in a temp directory with uv calls mocked."""
    runner = CliRunner()
    with patch("sully.commands.init.uv") as mock_uv:
        mock_uv.ensure_uv.return_value = "/usr/bin/uv"
        args = ["init", name] + (extra_args or [])
        result = runner.invoke(cli, args, catch_exceptions=False)
    return result, tmp_path / name, mock_uv


def test_init_creates_project_structure(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    result, root, _ = _invoke_init(tmp_path)

    assert result.exit_code == 0
    assert root.is_dir()
    assert (root / "pyproject.toml").is_file()
    assert (root / "pyrightconfig.json").is_file()
    assert (root / "src" / "myapp" / "__init__.py").is_file()
    assert (root / "src" / "myapp" / "main.py").is_file()
    assert (root / "src" / "myapp" / "py.typed").is_file()
    assert (root / "tests" / "test_main.py").is_file()
    assert (root / ".gitignore").is_file()
    assert (root / "README.md").is_file()


def test_init_directory_already_exists(tmp_path: Path, monkeypatch: Path) -> None:
    """Should fail with a clear error if the directory already exists."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "myapp").mkdir()
    runner = CliRunner()
    with patch("sully.commands.init.uv"):
        result = runner.invoke(cli, ["init", "myapp"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_init_pyproject_content(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _invoke_init(tmp_path)
    content = (tmp_path / "myapp" / "pyproject.toml").read_text()

    assert 'name = "myapp"' in content
    assert "requires-python" in content
    assert "[tool.sully]" in content
    assert '[tool.sully.check]' in content
    assert 'mode = "strict"' in content
    assert "check-before-run = true" in content


def test_init_pyrightconfig_content(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _invoke_init(tmp_path)
    data = json.loads((tmp_path / "myapp" / "pyrightconfig.json").read_text())

    assert data["typeCheckingMode"] == "strict"
    assert data["include"] == ["src"]
    assert data["pythonVersion"] == "3.12"


def test_init_custom_python_version(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    result, root, mock_uv = _invoke_init(tmp_path, extra_args=["--python", "3.11"])

    assert result.exit_code == 0
    data = json.loads((root / "pyrightconfig.json").read_text())
    assert data["pythonVersion"] == "3.11"

    content = (root / "pyproject.toml").read_text()
    assert ">=3.11" in content

    mock_uv.pin_python.assert_called_once_with("3.11", cwd=root)


def test_init_calls_uv_pin_and_sync(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _, root, mock_uv = _invoke_init(tmp_path)

    mock_uv.ensure_uv.assert_called_once()
    mock_uv.pin_python.assert_called_once_with("3.12", cwd=root)
    mock_uv.sync.assert_called_once_with(cwd=root)


def test_init_generated_main_is_typed(tmp_path: Path, monkeypatch: Path) -> None:
    """Generated main.py should have type annotations."""
    monkeypatch.chdir(tmp_path)
    _invoke_init(tmp_path)
    content = (tmp_path / "myapp" / "src" / "myapp" / "main.py").read_text()

    assert "def greet(name: str" in content
    assert "-> str:" in content
    assert "def main() -> None:" in content


def test_init_generated_test_imports_from_package(tmp_path: Path, monkeypatch: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _invoke_init(tmp_path)
    content = (tmp_path / "myapp" / "tests" / "test_main.py").read_text()

    assert "from myapp.main import greet" in content
    assert "def test_greet_default" in content


def test_init_hyphenated_name(tmp_path: Path, monkeypatch: Path) -> None:
    """Hyphens in project name should become underscores in package name."""
    monkeypatch.chdir(tmp_path)
    _invoke_init(tmp_path, name="my-app")
    root = tmp_path / "my-app"

    assert (root / "src" / "my_app" / "__init__.py").is_file()
    assert (root / "src" / "my_app" / "main.py").is_file()

    content = (root / "pyproject.toml").read_text()
    assert 'main = "src/my_app/main.py"' in content
