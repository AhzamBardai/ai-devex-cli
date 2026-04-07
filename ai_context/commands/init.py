"""Scaffold the .ai/ folder convention in a repository."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

MEMORY_MD_CONTENT = """# Memory Index

This file indexes all memory files in `.ai/memory/`. Each entry points to a file
that contains context for AI coding agents.

<!-- Add entries below as you create memory files -->
<!-- Format: - [Title](filename.md) — one-line description -->
"""

AGENTS_MD_CONTENT = """# Agent Context

This repository uses the `.ai/` convention for AI agent context.

## Quick Start for Agents

1. Read `.ai/memory/MEMORY.md` for an index of all context files
2. Review `.ai/rules/` for coding standards and constraints
3. Check `.ai/skills/` for reusable task patterns

## Memory Files

See `.ai/memory/MEMORY.md` for the full index.

## Skills

See `.ai/skills/` for available task patterns.
"""

AI_CONTEXT_TOML_CONTENT = """[project]
version = "1.0"
project_name = ""
default_model = "haiku"
max_tokens = 4000
template = "minimal"
"""

ARCHITECTURE_TEMPLATE = """# Architecture

## Overview

<!-- Describe the system at a high level: what it does and why it exists. -->

## Key Services

<!-- List the main components/services and their responsibilities. -->

## Data Flow

<!-- Describe how data moves through the system. -->

## Dependencies

<!-- List external dependencies (databases, message brokers, APIs, etc.). -->
"""

CONVENTIONS_TEMPLATE = """# Conventions

## Logging

<!-- Describe the logging library and pattern used. -->

## Model Validation

<!-- Describe how data validation/serialization is done. -->

## Test Structure

<!-- Describe how tests are organized and what patterns are used. -->
"""

TEAM_STANDARDS_TEMPLATE = """# Team Standards

## Code Review

- All PRs require at least one approval before merge
- CI must pass before merging

## Branching

- Feature branches: `feat/<ticket>-<short-description>`
- Hotfix branches: `fix/<ticket>-<short-description>`

## Naming

<!-- Add team-specific naming conventions here. -->
"""


def run_init(
    template: Literal["minimal", "full", "team"] = "minimal",
    no_agents_md: bool = False,
    path: Path = Path("."),
) -> list[str]:
    """Scaffold .ai/ folder structure. Idempotent — skips files that already exist.

    Args:
        template: Scaffold size. "minimal" creates the base structure,
                  "full" adds architecture and conventions templates,
                  "team" adds team standards rules file.
        no_agents_md: Skip creating AGENTS.md.
        path: Root directory to scaffold into.

    Returns:
        List of relative file paths that were created (empty if all existed).
    """
    created: list[str] = []
    ai_dir = path / ".ai"

    (ai_dir / "memory").mkdir(parents=True, exist_ok=True)
    (ai_dir / "rules").mkdir(parents=True, exist_ok=True)
    (ai_dir / "skills").mkdir(parents=True, exist_ok=True)

    memory_md = ai_dir / "memory" / "MEMORY.md"
    if not memory_md.exists():
        memory_md.write_text(MEMORY_MD_CONTENT)
        created.append(str(memory_md.relative_to(path)))

    for gitkeep in [ai_dir / "rules" / ".gitkeep", ai_dir / "skills" / ".gitkeep"]:
        if not gitkeep.exists():
            gitkeep.touch()
            created.append(str(gitkeep.relative_to(path)))

    if not no_agents_md:
        agents_md = path / "AGENTS.md"
        if not agents_md.exists():
            agents_md.write_text(AGENTS_MD_CONTENT)
            created.append("AGENTS.md")

    config_toml = path / "ai-context.toml"
    if not config_toml.exists():
        config_toml.write_text(AI_CONTEXT_TOML_CONTENT)
        created.append("ai-context.toml")

    if template in ("full", "team"):
        arch = ai_dir / "memory" / "architecture.md"
        if not arch.exists():
            arch.write_text(ARCHITECTURE_TEMPLATE)
            created.append(str(arch.relative_to(path)))

        conv = ai_dir / "memory" / "conventions.md"
        if not conv.exists():
            conv.write_text(CONVENTIONS_TEMPLATE)
            created.append(str(conv.relative_to(path)))

    if template == "team":
        standards = ai_dir / "rules" / "team-standards.md"
        if not standards.exists():
            standards.write_text(TEAM_STANDARDS_TEMPLATE)
            created.append(str(standards.relative_to(path)))

    return created
