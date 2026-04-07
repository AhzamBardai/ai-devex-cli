# Architecture

## Overview

`ai-context` is a single-binary CLI tool built with Typer. It has no server component and no database. All five commands operate on the local filesystem; only `generate` makes external network calls (to the Claude API).

## Component Diagram

```
User
 │
 ▼
ai-context CLI (Typer / main.py)
 │
 ├── init ──────────► commands/init.py
 │                    └── writes .ai/ scaffold (MEMORY.md, rules/, skills/, AGENTS.md, ai-context.toml)
 │
 ├── generate ──────► commands/generate.py
 │                    ├── generator.FileSelector
 │                    │   └── globs repo, scores by priority, respects .gitignore, caps by token budget
 │                    ├── generator.build_context_prompt
 │                    │   └── formats selected files into a single prompt string
 │                    ├── generator.generate_architecture ──► Claude API (tool_use forced)
 │                    ├── generator.generate_conventions  ──► Claude API (tool_use forced)
 │                    └── generator.generate_skills       ──► Claude API (tool_use forced)
 │
 ├── validate ──────► validator.validate_ai_folder
 │                    ├── checks MEMORY.md links resolve
 │                    ├── checks skill frontmatter (name, description)
 │                    └── checks architecture.md has required sections
 │
 ├── diff ──────────► commands/diff.py
 │                    ├── git diff HEAD -- .ai/    (changed files)
 │                    └── git diff --name-status   (new files not in architecture.md)
 │
 └── stats ─────────► commands/stats.py
                       └── scans .ai/ for file counts, token estimates, CHANGELOG sessions
```

## Data Flow (generate command)

```
1. User: ai-context generate --focus architecture --model haiku
2. FileSelector: glob repo → score by priority → cap at max_tokens → [(Path, content), ...]
3. build_context_prompt: format files → "Here are the key files:\n--- main.py ---\n..."
4. generate_architecture: Claude API call with ARCHITECTURE_TOOL forced
5. Claude: returns tool_use block with input matching ARCHITECTURE_TOOL schema
6. _parse_architecture_output: dict → ArchitectureDoc (Pydantic validates)
7. architecture_to_markdown: ArchitectureDoc → markdown string
8. write_output: write to .ai/memory/architecture.md
```

## Key Design Decisions

- [ADR 001](adr/001-llm-provider-choice.md) — Why Anthropic Claude (forced tool_use, cost, reliability)
- [ADR 002](adr/002-structured-output-schema-design.md) — Why forced tool_use over JSON mode
