"""Tests for sully.uv — uv subprocess wrapper."""

from unittest.mock import patch

import pytest

from sully import uv


def test_ensure_uv_found() -> None:
    """Should return a path string when uv is installed."""
    result = uv.ensure_uv()
    assert result is not None
    assert "uv" in result


def test_ensure_uv_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should sys.exit with a helpful message when uv is missing."""
    monkeypatch.setattr("shutil.which", lambda _name: None)
    with pytest.raises(SystemExit) as exc_info:
        uv.ensure_uv()
    # sys.exit with a string sets code to 1 and prints the string
    assert "uv is not installed" in str(exc_info.value)


def test_add_builds_dev_args() -> None:
    """Should pass --dev flag to uv add."""
    with patch.object(uv, "_run") as mock_run:
        uv.add(["requests"], dev=True)
        mock_run.assert_called_once_with(["add", "--dev", "requests"], cwd=None)


def test_add_builds_group_args() -> None:
    """Should pass --group flag to uv add."""
    with patch.object(uv, "_run") as mock_run:
        uv.add(["pytest"], group="test")
        mock_run.assert_called_once_with(["add", "--group", "test", "pytest"], cwd=None)


def test_add_plain() -> None:
    """No flags when neither dev nor group."""
    with patch.object(uv, "_run") as mock_run:
        uv.add(["flask"])
        mock_run.assert_called_once_with(["add", "flask"], cwd=None)


def test_add_multiple_packages() -> None:
    """Should pass all packages to uv add."""
    with patch.object(uv, "_run") as mock_run:
        uv.add(["flask", "requests", "click"])
        mock_run.assert_called_once_with(["add", "flask", "requests", "click"], cwd=None)


def test_remove_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.remove(["requests"])
        mock_run.assert_called_once_with(["remove", "requests"], cwd=None)


def test_sync_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.sync()
        mock_run.assert_called_once_with(["sync"], cwd=None)


def test_run_script_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.run_script("main.py")
        mock_run.assert_called_once_with(["run", "python", "main.py"], cwd=None, check=False)


def test_run_cmd_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.run_cmd(["pyright", "--level=strict"])
        mock_run.assert_called_once_with(
            ["run", "pyright", "--level=strict"], cwd=None, check=True
        )


def test_pin_python_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.pin_python("3.12")
        mock_run.assert_called_once_with(["python", "pin", "3.12"], cwd=None)


def test_python_install_args() -> None:
    with patch.object(uv, "_run") as mock_run:
        uv.python_install("3.12")
        mock_run.assert_called_once_with(["python", "install", "3.12"], cwd=None)


def test_dev_flag_takes_precedence_over_group() -> None:
    """When both dev and group are set, dev should win (they're elif)."""
    with patch.object(uv, "_run") as mock_run:
        uv.add(["pkg"], dev=True, group="test")
        args = mock_run.call_args[0][0]
        assert "--dev" in args
        assert "--group" not in args
