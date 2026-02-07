"""Parse [tool.sully] from pyproject.toml."""

from pathlib import Path

import tomlkit


def find_pyproject(start: Path | None = None) -> Path:
    """Walk up from *start* (default: cwd) to find pyproject.toml."""
    current = (start or Path.cwd()).resolve()
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise FileNotFoundError("No pyproject.toml found in any parent directory.")


def load(start: Path | None = None) -> dict:
    """Return the [tool.sully] table, or {} if absent."""
    path = find_pyproject(start)
    doc = tomlkit.loads(path.read_text())
    return doc.get("tool", {}).get("sully", {})


def load_full(start: Path | None = None) -> tomlkit.TOMLDocument:
    """Return the full parsed pyproject.toml as a TOMLDocument."""
    path = find_pyproject(start)
    return tomlkit.loads(path.read_text())


def get_main_script(start: Path | None = None) -> str | None:
    """Return the configured main script path, or None."""
    cfg = load(start)
    return cfg.get("main")


def get_check_config(start: Path | None = None) -> dict:
    """Return [tool.sully.check] config with defaults."""
    cfg = load(start)
    check = cfg.get("check", {})
    return {
        "mode": check.get("mode", "strict"),
        "check-before-run": check.get("check-before-run", True),
    }


def get_doc_config(start: Path | None = None) -> dict:
    """Return [tool.sully.doc] config with defaults."""
    cfg = load(start)
    doc = cfg.get("doc", {})
    return {
        "output": doc.get("output", "docs"),
        "doc-before-run": doc.get("doc-before-run", True),
    }
