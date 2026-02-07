"""Tests for sully.config — pyproject.toml parsing and error handling."""

import os
from pathlib import Path

import pytest

from sully import config


def test_find_pyproject_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should raise FileNotFoundError when no pyproject.toml exists anywhere."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="No pyproject.toml found"):
        config.find_pyproject()


def test_find_pyproject_in_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should find pyproject.toml in the current directory."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    monkeypatch.chdir(tmp_path)
    assert config.find_pyproject() == tmp_path / "pyproject.toml"


def test_find_pyproject_walks_up(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should find pyproject.toml in a parent directory."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert config.find_pyproject() == tmp_path / "pyproject.toml"


def test_load_no_tool_sully_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should return {} when [tool.sully] is missing."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    monkeypatch.chdir(tmp_path)
    assert config.load() == {}


def test_load_empty_tool_sully(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should return {} when [tool.sully] exists but is empty."""
    (tmp_path / "pyproject.toml").write_text("[tool.sully]\n")
    monkeypatch.chdir(tmp_path)
    result = config.load()
    assert dict(result) == {}


def test_load_with_main_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.sully]\nmain = "src/app/main.py"\n'
    )
    monkeypatch.chdir(tmp_path)
    cfg = config.load()
    assert cfg["main"] == "src/app/main.py"


def test_get_main_script_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Should return None when main is not configured."""
    (tmp_path / "pyproject.toml").write_text("[tool.sully]\n")
    monkeypatch.chdir(tmp_path)
    assert config.get_main_script() is None


def test_get_main_script_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.sully]\nmain = "src/app/main.py"\n'
    )
    monkeypatch.chdir(tmp_path)
    assert config.get_main_script() == "src/app/main.py"


def test_get_check_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without [tool.sully.check], defaults should be strict + check-before-run."""
    (tmp_path / "pyproject.toml").write_text("[tool.sully]\n")
    monkeypatch.chdir(tmp_path)
    cfg = config.get_check_config()
    assert cfg["mode"] == "strict"
    assert cfg["check-before-run"] is True


def test_get_check_config_custom(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.sully.check]\nmode = "basic"\ncheck-before-run = false\n'
    )
    monkeypatch.chdir(tmp_path)
    cfg = config.get_check_config()
    assert cfg["mode"] == "basic"
    assert cfg["check-before-run"] is False


def test_get_check_config_mode_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.sully.check]\nmode = "off"\n'
    )
    monkeypatch.chdir(tmp_path)
    cfg = config.get_check_config()
    assert cfg["mode"] == "off"


def test_load_full_returns_entire_document(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'hello'\n\n[tool.sully]\nmain = 'x.py'\n"
    )
    monkeypatch.chdir(tmp_path)
    doc = config.load_full()
    assert doc["project"]["name"] == "hello"
    assert doc["tool"]["sully"]["main"] == "x.py"


def test_find_pyproject_no_pyproject_in_empty_tree(tmp_path: Path) -> None:
    """Explicit start path with no pyproject.toml anywhere above."""
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        config.find_pyproject(start=deep)
