# Makefile for sully

.PHONY: help build clean test install uninstall

help:
	@echo "Makefile for sully"
	@echo ""
	@echo "Usage:"
	@echo "  make install    - Install sully locally (editable)"
	@echo "  make uninstall  - Uninstall sully"
	@echo "  make build      - Build the package"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make test       - Run tests"

install:
	uv pip install -e .

uninstall:
	uv pip uninstall sully

build:
	python -m build

clean:
	rm -rf build dist *.egg-info

test:
	pytest tests/
