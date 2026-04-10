.PHONY: install dev test lint format typecheck ci clean docs build publish

install:  ## Install package
	pip install -e .

dev:  ## Install with dev dependencies
	pip install -e ".[dev,export,compliance]"
	pre-commit install

test:  ## Run test suite
	python -m pytest tests/ -q --tb=short

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=faircareai --cov-report=term-missing --cov-report=html

lint:  ## Run linter
	ruff check src/ tests/

format:  ## Format code
	ruff format src/ tests/

typecheck:  ## Run type checker
	mypy src/faircareai/

ci: lint typecheck test  ## Run full CI pipeline locally

clean:  ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info .pytest_cache .mypy_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:  ## Build package
	python -m build
	twine check dist/*

dashboard:  ## Launch Streamlit dashboard
	faircareai dashboard

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
