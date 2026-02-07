# sully

**Production-ready Python, from the first line.**

sully is the layer between you and Python that enforces the practices production code demands — types, tests, docs, structure — so you build intentionally from day one instead of bolting quality on later.


## Why sully?

Most Python projects start loose and add guardrails later — type hints after the prototype, tests after the bug, docs after the deadline. sully flips that. It scaffolds projects with strict types, test stubs, and doc generation from the start, then refuses to run code that doesn't pass muster.

- **Intentional by design** — pyright strict mode is the default, not an afterthought
- **Guardrails, not suggestions** — `sully run` won't execute code with type errors
- **Production-grade scaffolding** — `sully init` generates a fully typed project with tests, docs config, and PEP 561 markers
- **Ship with confidence** — types, tests, and docs are enforced from the first commit

## Features

- **Type enforcement** — pyright strict mode by default; `sully run` blocks execution until types pass
- **Built on uv** — fast dependency management, no pip
- **Opinionated structure** — every project starts with types, tests, docs, and a clean layout
- **One config file** — everything in `pyproject.toml` under `[tool.sully]`

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

```
uv pip install sully
```

Or for development:

```
git clone https://github.com/viraatdas/sully.git
cd sully
uv pip install -e .
```

## Quick Start

```bash
sully init my_app --python 3.12
cd my_app
sully check       # run pyright
sully run          # type-check then run
sully test         # run pytest
sully doc          # generate docs
```

## Commands

| Command | Description |
|---------|-------------|
| `sully init <name> [--python 3.12]` | Create a new typed Python project |
| `sully add <pkg> [--dev] [--group G]` | Add dependency via `uv add` |
| `sully remove <pkg>` | Remove dependency via `uv remove` |
| `sully sync` | Install all deps via `uv sync` |
| `sully check` | Run pyright type checker |
| `sully run [--no-check]` | Type-check then run main script |
| `sully test [--generate]` | Run pytest; `--generate` creates test stubs |
| `sully doc` | Generate docs via pdoc |

## Type Enforcement

The core feature. By default every project uses pyright in strict mode.

`sully run` runs `sully check` first and won't execute if types fail. Pass `--no-check` to bypass.

Configure in `pyproject.toml`:

```toml
[tool.sully.check]
mode = "strict"           # "off", "basic", "standard", "strict"
check-before-run = true
```

## Generated Project Structure

```
my_app/
├── pyproject.toml
├── pyrightconfig.json
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── main.py
│       └── py.typed
├── tests/
│   └── test_main.py
├── .python-version
├── .gitignore
└── README.md
```

## License

Apache 2.0
