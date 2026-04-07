# ai-context

Scaffold, validate, and AI-generate the `.ai/` context convention for any repo. One command to give every AI coding agent a shared understanding of your codebase.

[![CI](https://github.com/AhzamBardai/ai-devex-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/AhzamBardai/ai-devex-cli/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/AhzamBardai/ai-devex-cli/badge.svg)](https://codecov.io/gh/AhzamBardai/ai-devex-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Every developer using AI coding agents (Claude Code, Cursor, Copilot, Gemini CLI) starts from scratch: no shared context, no conventions, no memory of what the codebase does. Each agent invocation is stateless.

`ai-context` solves this by productizing the `.ai/` folder convention — a lightweight directory that holds structured memory, skills, and rules for any AI agent that understands it. Run `ai-context init` to scaffold it, `ai-context generate` to let Claude analyze your codebase and fill in the context automatically, and `ai-context validate` to keep it consistent.

The tool has no server, no account requirement, and no telemetry by default. It works with any repo in any language.

## Architecture

```
ai-context CLI
├── init         → scaffold .ai/ folder (idempotent, < 100ms)
├── generate     → AI analysis → .ai/memory/architecture.md + conventions.md + skills/
├── validate     → lint .ai/ against convention schema
├── diff         → detect stale context after refactors
└── stats        → report memory files, skills, and token counts
```

See [docs/architecture.md](docs/architecture.md) for the full component diagram and data flow.

## Use Cases

**Use Case 1 — Scaffold and generate context for a Python microservice:**

A developer runs `ai-context init && ai-context generate --focus architecture` in a Kafka consumer service. The tool identifies it as a Kafka→Elasticsearch pipeline and generates `architecture.md` with Overview, Key Services, Data Flow, and Dependencies in under 30 seconds for under $0.01.

```
$ ai-context init
✓ Created .ai/memory/MEMORY.md
✓ Created .ai/rules/.gitkeep
✓ Created .ai/skills/.gitkeep
✓ Created AGENTS.md
✓ Created ai-context.toml

$ ai-context generate --focus architecture
Analyzing repo...

Generated:
  .ai/memory/architecture.md  (310 tokens)

Review and edit before committing. Run ai-context validate to check.

$ ai-context validate
✓ Validation passed.
```

**Use Case 2 — Detect stale context after a refactor:**

After adding `notifier.py` to the repo, `ai-context diff` detects that `architecture.md` doesn't mention `NotifierService`:

```
$ ai-context diff
⚠ .ai/memory/architecture.md may be stale — new file notifier.py not reflected
  → Run `ai-context generate --focus architecture` to update
```

## Quick Start

```bash
pip install ai-context
export ANTHROPIC_API_KEY=sk-ant-...

cd my-project
ai-context init
ai-context generate --focus architecture
ai-context validate
```

## Commands

| Command | Description |
|---------|-------------|
| `ai-context init [--template minimal\|full\|team]` | Scaffold `.ai/` folder |
| `ai-context generate [--model haiku\|sonnet] [--focus architecture\|conventions\|skills\|all]` | AI-generate context |
| `ai-context validate [--path .]` | Lint `.ai/` against schema |
| `ai-context diff [--path .]` | Show stale context vs git HEAD |
| `ai-context stats [--path .]` | Report memory file count and token usage |

### Templates

| Template | Creates |
|----------|---------|
| `minimal` (default) | `MEMORY.md`, empty `rules/`, `skills/`, `AGENTS.md`, `ai-context.toml` |
| `full` | minimal + `architecture.md` and `conventions.md` templates |
| `team` | full + `rules/team-standards.md` template |

## Configuration

`ai-context` reads `ai-context.toml` created by `init`:

```toml
[project]
default_model = "haiku"     # or "sonnet" for higher quality
max_tokens = 4000           # token budget for codebase file selection
```

**Required for `generate`:** `ANTHROPIC_API_KEY` environment variable.

If `ANTHROPIC_API_KEY` is not set, `generate` exits with a clear error. All other commands work without it.

## Benchmarks / Results

| Metric | Target | Result |
|--------|--------|--------|
| `init` latency | < 100ms | ~5ms |
| `generate` latency (medium repo, haiku) | < 30s | ~8s |
| Cost per medium repo (haiku) | < $0.01 | ~$0.001 |
| Structured output Pydantic failures | 0 across 10 runs | 0 |
| Architecture recall (key services) | ≥ 0.80 | ≥ 0.85 |
| Unit test coverage | ≥ 85% | 86% |

See [results/cost-by-repo-size.md](results/cost-by-repo-size.md) for detailed cost breakdown by repo size tier.

## Design Decisions

- [ADR 001 — LLM Provider Choice](docs/adr/001-llm-provider-choice.md): Why Anthropic Claude with forced tool_use
- [ADR 002 — Structured Output Schema Design](docs/adr/002-structured-output-schema-design.md): Why one tool per focus over JSON mode

## Development

```bash
git clone https://github.com/AhzamBardai/ai-devex-cli.git
cd ai-devex-cli
make install

make test            # unit tests (86% coverage, no API key needed)
make test-all        # unit + integration (requires ANTHROPIC_API_KEY)
make test-scenarios  # use case integration tests
make eval            # behavioral eval suite (quality, reliability, cost)
make lint            # ruff lint + format check
make type-check      # mypy
```
