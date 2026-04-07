# Contributing

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
make test          # unit tests only
make test-all      # unit + integration (requires ANTHROPIC_API_KEY)
make eval          # behavioral eval suite
```

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`

Types: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`, `perf`, `ci`

## Pull Requests

- All PRs require passing CI (lint + type check + unit tests + ≥85% coverage)
- Integration tests run on merge to main only
- Link any relevant issues in the PR description
