.PHONY: install test test-all test-scenarios eval lint format type-check clean publish up

install:
	pip install -e ".[dev]"

test:
	pytest tests/unit/ -v --cov=ai_context --cov-report=term-missing

test-all:
	pytest tests/unit/ tests/integration/ -v -m "not eval"

test-scenarios:
	pytest tests/integration/ -m use_case -v

eval:
	pytest tests/eval/ -v -m eval --tb=short

lint:
	ruff check ai_context/ tests/
	ruff format --check ai_context/ tests/

format:
	ruff format ai_context/ tests/
	ruff check --fix ai_context/ tests/

type-check:
	mypy ai_context/ --ignore-missing-imports

up:
	@echo "No local services required."
	@echo "Run 'make install' then 'ai-context --help'"

clean:
	rm -rf dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ coverage.xml

publish:
	pip install build twine
	python -m build
	twine upload dist/*
