"""Tests for sully commands — error paths and edge cases."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from sully.cli import cli


# ---------------------------------------------------------------------------
# sully check
# ---------------------------------------------------------------------------

class TestCheck:
    def test_check_mode_off(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When mode='off', should skip pyright entirely."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully.check]\nmode = "off"\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        with patch("sully.commands.check.uv") as mock_uv:
            result = runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "disabled" in result.output
        mock_uv.run_cmd.assert_not_called()

    def test_check_pyright_fails(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should exit non-zero and print failure message when pyright fails."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully.check]\nmode = "strict"\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=1)
        with patch("sully.commands.check.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            result = runner.invoke(cli, ["check"])
        assert result.exit_code != 0
        assert "type errors found" in result.output.lower()

    def test_check_pyright_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully.check]\nmode = "strict"\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.check.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            result = runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "all clear" in result.output.lower()

    def test_check_uses_configured_mode(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should pass the configured mode to pyright --level."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully.check]\nmode = "basic"\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.check.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            runner.invoke(cli, ["check"])
            args = mock_uv.run_cmd.call_args[0][0]
            assert "--level=basic" in args

    def test_check_no_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should error when no pyproject.toml exists."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["check"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# sully run
# ---------------------------------------------------------------------------

class TestRun:
    def test_run_no_main_script_configured(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should error when [tool.sully] main is not set."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully.check]\nmode = "off"\n\n'
            '[tool.sully.doc]\ndoc-before-run = false\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0
        assert "No main script configured" in result.output

    def test_run_no_check_flag_skips_type_check(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--no-check should skip pyright even when check-before-run is true."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "strict"\ncheck-before-run = true\n\n'
            '[tool.sully.doc]\ndoc-before-run = false\n'
        )
        (tmp_path / "main.py").write_text("print('hi')\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv:
            mock_uv.run_script.return_value = mock_result
            result = runner.invoke(cli, ["run", "--no-check"])

        # pyright should NOT have been called
        mock_uv.run_cmd.assert_not_called()
        mock_uv.run_script.assert_called_once_with("main.py")

    def test_run_type_check_fails_blocks_execution(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When type check fails, the script should NOT run."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "strict"\ncheck-before-run = true\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_fail = MagicMock(returncode=1)
        with patch("sully.commands.run.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_fail
            result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0
        assert "fix before running" in result.output.lower()
        mock_uv.run_script.assert_not_called()

    def test_run_check_mode_off_skips_gate(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When mode='off', run should not invoke pyright at all."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "off"\ncheck-before-run = true\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv:
            mock_uv.run_script.return_value = mock_result
            result = runner.invoke(cli, ["run"])
        mock_uv.run_cmd.assert_not_called()

    def test_run_check_before_run_false(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When check-before-run=false, run should skip the gate."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "strict"\ncheck-before-run = false\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv:
            mock_uv.run_script.return_value = mock_result
            result = runner.invoke(cli, ["run"])
        mock_uv.run_cmd.assert_not_called()

    def test_run_doc_gate_fails_blocks_execution(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When doc generation fails, the script should NOT run."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "off"\n\n'
            '[tool.sully.doc]\ndoc-before-run = true\n'
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_fail = MagicMock(returncode=1)
        with patch("sully.commands.run.uv") as mock_uv, \
             patch("sully.commands.doc.uv") as mock_doc_uv:
            mock_doc_uv.run_cmd.return_value = mock_fail
            result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0
        assert "doc generation failed" in result.output.lower()
        mock_uv.run_script.assert_not_called()

    def test_run_no_doc_flag_skips_doc_gate(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--no-doc should skip doc generation."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "off"\n\n'
            '[tool.sully.doc]\ndoc-before-run = true\n'
        )
        (tmp_path / "main.py").write_text("print('hi')\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv, \
             patch("sully.commands.doc.uv") as mock_doc_uv:
            mock_uv.run_script.return_value = mock_result
            result = runner.invoke(cli, ["run", "--no-doc"])
        mock_doc_uv.run_cmd.assert_not_called()
        mock_uv.run_script.assert_called_once_with("main.py")

    def test_run_doc_before_run_false_skips_gate(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When doc-before-run=false, run should skip the doc gate."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "off"\n\n'
            '[tool.sully.doc]\ndoc-before-run = false\n'
        )
        (tmp_path / "main.py").write_text("print('hi')\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv, \
             patch("sully.commands.doc.uv") as mock_doc_uv:
            mock_uv.run_script.return_value = mock_result
            result = runner.invoke(cli, ["run"])
        mock_doc_uv.run_cmd.assert_not_called()

    def test_run_doc_gate_passes_then_runs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When doc generation passes, the script should run."""
        (tmp_path / "pyproject.toml").write_text(
            '[tool.sully]\nmain = "main.py"\n\n'
            '[tool.sully.check]\nmode = "off"\n\n'
            '[tool.sully.doc]\ndoc-before-run = true\n'
        )
        (tmp_path / "main.py").write_text("print('hi')\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_ok = MagicMock(returncode=0)
        with patch("sully.commands.run.uv") as mock_uv, \
             patch("sully.commands.doc.uv") as mock_doc_uv:
            mock_doc_uv.run_cmd.return_value = mock_ok
            mock_uv.run_script.return_value = mock_ok
            result = runner.invoke(cli, ["run"])
        mock_doc_uv.run_cmd.assert_called_once()
        mock_uv.run_script.assert_called_once_with("main.py")

    def test_run_no_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should error when no pyproject.toml exists."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["run"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# sully test
# ---------------------------------------------------------------------------

class TestTest:
    def test_test_generate_no_src_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--generate should error if there's no src/ directory."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])
        assert result.exit_code != 0
        assert "No src/ directory" in result.output

    def test_test_generate_creates_stubs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should create test stubs for public functions in src/."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src" / "mymod"
        src.mkdir(parents=True)
        (src / "hello.py").write_text(
            "def greet() -> str:\n    return 'hi'\n\ndef farewell() -> str:\n    return 'bye'\n"
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        assert result.exit_code == 0
        test_file = tmp_path / "tests" / "test_mymod_hello.py"
        assert test_file.is_file()
        content = test_file.read_text()
        assert "from mymod.hello import greet, farewell" in content
        assert "def test_greet" in content
        assert "def test_farewell" in content

    def test_test_generate_skips_private_functions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Private functions (starting with _) should not get test stubs."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text(
            "def public() -> None: ...\ndef _private() -> None: ...\n"
        )
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        test_file = tmp_path / "tests" / "test_mod.py"
        content = test_file.read_text()
        assert "test_public" in content
        assert "_private" not in content

    def test_test_generate_skips_dunder_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """__init__.py and other _-prefixed files should be skipped."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src" / "pkg"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text("def init_func() -> None: ...\n")
        (src / "core.py").write_text("def do_stuff() -> None: ...\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        # Should NOT create a test for __init__.py
        assert not (tmp_path / "tests" / "test_pkg___init__.py").exists()
        # Should create a test for core.py
        assert (tmp_path / "tests" / "test_pkg_core.py").is_file()

    def test_test_generate_skips_existing_test_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should not overwrite existing test files."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src"
        src.mkdir()
        (src / "mod.py").write_text("def func() -> None: ...\n")
        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_mod.py").write_text("# my custom tests\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        assert "skip test_mod.py (exists)" in result.output
        # Should NOT overwrite
        assert (tests / "test_mod.py").read_text() == "# my custom tests\n"

    def test_test_generate_handles_syntax_errors(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Files with syntax errors should be silently skipped."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src"
        src.mkdir()
        (src / "broken.py").write_text("def oops(\n")  # syntax error
        (src / "good.py").write_text("def works() -> None: ...\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        assert result.exit_code == 0
        assert not (tmp_path / "tests" / "test_broken.py").exists()
        assert (tmp_path / "tests" / "test_good.py").is_file()

    def test_test_generate_no_public_functions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Files with only private functions should not produce test stubs."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
        src = tmp_path / "src"
        src.mkdir()
        (src / "internal.py").write_text("def _helper() -> None: ...\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["test", "--generate"])

        assert result.exit_code == 0
        assert "Generated 0 test file(s)" in result.output
        assert not (tmp_path / "tests" / "test_internal.py").exists()


# ---------------------------------------------------------------------------
# sully sync
# ---------------------------------------------------------------------------

class TestSync:
    def test_sync_calls_uv(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        with patch("sully.commands.sync.uv") as mock_uv:
            result = runner.invoke(cli, ["sync"])
        assert result.exit_code == 0
        mock_uv.sync.assert_called_once()
        assert "synced" in result.output.lower()


# ---------------------------------------------------------------------------
# sully doc
# ---------------------------------------------------------------------------

class TestDoc:
    def test_doc_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should report error when pdoc fails."""
        (tmp_path / "pyproject.toml").write_text("[tool.sully.doc]\noutput = 'docs'\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=1)
        with patch("sully.commands.doc.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            result = runner.invoke(cli, ["doc"])
        assert result.exit_code != 0
        assert "pdoc failed" in result.output

    def test_doc_success(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "pyproject.toml").write_text("[tool.sully.doc]\noutput = 'apidocs'\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.doc.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            result = runner.invoke(cli, ["doc"])
        assert result.exit_code == 0
        assert "apidocs" in result.output

    def test_doc_default_output_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should default to 'docs' when [tool.sully.doc] output is not set."""
        (tmp_path / "pyproject.toml").write_text("[tool.sully]\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        mock_result = MagicMock(returncode=0)
        with patch("sully.commands.doc.uv") as mock_uv:
            mock_uv.run_cmd.return_value = mock_result
            runner.invoke(cli, ["doc"])
            args = mock_uv.run_cmd.call_args[0][0]
            assert "--output-directory=docs" in args

    def test_doc_no_pyproject(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should error when no pyproject.toml exists."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(cli, ["doc"])
        assert result.exit_code != 0
