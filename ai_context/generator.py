"""File selection, prompt building, and Claude API integration for the generate command."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pathspec
import structlog

log = structlog.get_logger()

SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "coverage",
        "htmlcov",
        ".ai",
    }
)

SOURCE_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".ts", ".tsx", ".js", ".jsx", ".kt", ".java", ".go", ".rs", ".rb", ".cs"}
)


def estimate_tokens(text: str) -> int:
    """Estimate token count using chars/4 approximation."""
    return len(text) // 4


def _priority_score(path: Path, root: Path) -> int:
    """Higher score = higher priority for file selection."""
    name = path.name.lower()
    rel = str(path.relative_to(root)).lower()

    if name.startswith("readme"):
        return 100
    if name in {"pyproject.toml", "package.json", "build.gradle.kts", "build.gradle", "pom.xml", "setup.py"}:
        return 90
    if name in {"main.py", "app.py", "index.py", "server.py", "index.ts", "index.js", "main.kt"}:
        return 80
    if "config" in name or name == "makefile":
        return 70
    if name.endswith((".toml", ".yaml", ".yml")):
        return 60
    if path.suffix in SOURCE_EXTENSIONS and "test" not in rel and "spec" not in rel:
        return 50
    if "test" in rel or "spec" in rel:
        return 30
    return 10


class FileSelector:
    """Selects representative files within a token budget, respecting .gitignore.

    Args:
        root: Root directory of the repository.
        max_tokens: Maximum tokens to include across all selected files.
    """

    def __init__(self, root: Path, max_tokens: int = 4000) -> None:
        self.root = root
        self.max_tokens = max_tokens
        self._spec = self._load_gitignore()

    def _load_gitignore(self) -> pathspec.PathSpec | None:
        gitignore = self.root / ".gitignore"
        if gitignore.exists():
            return pathspec.PathSpec.from_lines(
                "gitignore", gitignore.read_text().splitlines()
            )
        return None

    def _is_ignored(self, path: Path) -> bool:
        rel = path.relative_to(self.root)
        parts = rel.parts
        if any(part in SKIP_DIRS for part in parts):
            return True
        if self._spec and self._spec.match_file(str(rel)):
            return True
        return False

    def select(self) -> list[tuple[Path, str]]:
        """Select files within the token budget, ordered by priority.

        Returns:
            List of (path, content) tuples for selected files.
        """
        candidates: list[tuple[int, Path]] = []

        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if self._is_ignored(path):
                continue
            try:
                path.read_bytes()
            except (OSError, PermissionError):
                continue
            score = _priority_score(path, self.root)
            candidates.append((score, path))

        candidates.sort(key=lambda x: x[0], reverse=True)

        selected: list[tuple[Path, str]] = []
        tokens_used = 0

        for _, path in candidates:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, PermissionError):
                continue

            tokens = estimate_tokens(content)
            remaining = self.max_tokens - tokens_used

            if tokens > remaining:
                if remaining > 200:
                    content = content[: remaining * 4]
                    tokens = estimate_tokens(content)
                else:
                    continue

            selected.append((path, content))
            tokens_used += tokens

            if tokens_used >= self.max_tokens:
                break

        return selected


def build_context_prompt(files: list[tuple[Path, str]], root: Path) -> str:
    """Build a context prompt from selected files.

    Args:
        files: List of (path, content) tuples.
        root: Root directory used to compute relative paths.

    Returns:
        Formatted prompt string with file contents.
    """
    parts = ["Here are the key files from the repository:\n"]
    for path, content in files:
        rel = path.relative_to(root)
        parts.append(f"\n--- {rel} ---\n{content}\n")
    return "\n".join(parts)


# ── Claude tool schemas ──────────────────────────────────────────────────────

ARCHITECTURE_TOOL: dict[str, Any] = {
    "name": "generate_architecture",
    "description": "Generate structured architecture documentation for the codebase",
    "input_schema": {
        "type": "object",
        "properties": {
            "overview": {
                "type": "string",
                "description": "2-3 paragraph overview of the system",
            },
            "key_services": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "technology": {"type": "string"},
                    },
                    "required": ["name", "description"],
                },
            },
            "data_flow": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "sink": {"type": "string"},
                        "description": {"type": "string"},
                    },
                    "required": ["source", "sink", "description"],
                },
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["overview", "key_services", "data_flow", "dependencies"],
    },
}

CONVENTIONS_TOOL: dict[str, Any] = {
    "name": "generate_conventions",
    "description": "Generate structured conventions documentation for the codebase",
    "input_schema": {
        "type": "object",
        "properties": {
            "logging": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "example": {"type": "string"},
                },
                "required": ["name", "description"],
            },
            "model_validation": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "example": {"type": "string"},
                },
                "required": ["name", "description"],
            },
            "test_structure": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "example": {"type": "string"},
                },
                "required": ["name", "description"],
            },
            "additional": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "example": {"type": "string"},
                    },
                    "required": ["name", "description"],
                },
            },
        },
        "required": [],
    },
}

SKILLS_TOOL: dict[str, Any] = {
    "name": "generate_skills",
    "description": "Generate suggested skill patterns for AI coding agents in this repo",
    "input_schema": {
        "type": "object",
        "properties": {
            "skills": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "trigger": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name", "description", "trigger"],
                },
            }
        },
        "required": ["skills"],
    },
}

MODEL_MAP: dict[str, str] = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
}

# ── Parsers ──────────────────────────────────────────────────────────────────

from ai_context.schema import (  # noqa: E402
    ArchitectureDoc,
    Convention,
    ConventionsDoc,
    DataFlowStep,
    GenerateOutput,
    KeyService,
    SuggestedSkill,
)


def _parse_architecture_output(data: dict[str, Any]) -> ArchitectureDoc:
    """Parse Claude's tool output dict into an ArchitectureDoc."""
    return ArchitectureDoc(
        overview=data["overview"],
        key_services=[KeyService(**s) for s in data.get("key_services", [])],
        data_flow=[DataFlowStep(**f) for f in data.get("data_flow", [])],
        dependencies=data.get("dependencies", []),
    )


def _parse_conventions_output(data: dict[str, Any]) -> ConventionsDoc:
    """Parse Claude's tool output dict into a ConventionsDoc."""

    def _conv(d: dict[str, Any] | None) -> Convention | None:
        if not d:
            return None
        return Convention(
            name=d["name"], description=d["description"], example=d.get("example", "")
        )

    return ConventionsDoc(
        logging=_conv(data.get("logging")),
        model_validation=_conv(data.get("model_validation")),
        test_structure=_conv(data.get("test_structure")),
        additional=[
            Convention(
                name=c["name"], description=c["description"], example=c.get("example", "")
            )
            for c in data.get("additional", [])
        ],
    )


# ── Claude API calls ─────────────────────────────────────────────────────────


def generate_architecture(
    files: list[tuple[Path, str]],
    root: Path,
    model: str = "haiku",
) -> ArchitectureDoc:
    """Call Claude to generate architecture documentation with forced tool_use.

    Args:
        files: Selected file contents from FileSelector.
        root: Repository root for relative path computation.
        model: Model key ("haiku" or "sonnet").

    Returns:
        Parsed ArchitectureDoc from Claude's structured output.

    Raises:
        ValueError: If Claude does not return valid structured output.
    """
    import anthropic

    client = anthropic.Anthropic()
    context = build_context_prompt(files, root)

    response = client.messages.create(
        model=MODEL_MAP[model],
        max_tokens=2048,
        tools=[ARCHITECTURE_TOOL],  # type: ignore[list-item]
        tool_choice={"type": "tool", "name": "generate_architecture"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"{context}\n\nAnalyze this repository and generate comprehensive "
                    "architecture documentation. Identify all key services, data flows, "
                    "and external dependencies."
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_architecture":
            return _parse_architecture_output(block.input)  # type: ignore[arg-type]

    raise ValueError("Claude did not return structured architecture output")


def generate_conventions(
    files: list[tuple[Path, str]],
    root: Path,
    model: str = "haiku",
) -> ConventionsDoc:
    """Call Claude to generate conventions documentation with forced tool_use."""
    import anthropic

    client = anthropic.Anthropic()
    context = build_context_prompt(files, root)

    response = client.messages.create(
        model=MODEL_MAP[model],
        max_tokens=2048,
        tools=[CONVENTIONS_TOOL],  # type: ignore[list-item]
        tool_choice={"type": "tool", "name": "generate_conventions"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"{context}\n\nAnalyze this codebase's conventions: logging patterns, "
                    "data validation/serialization, and test structure. Document what you observe."
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_conventions":
            return _parse_conventions_output(block.input)  # type: ignore[arg-type]

    raise ValueError("Claude did not return structured conventions output")


def generate_skills(
    files: list[tuple[Path, str]],
    root: Path,
    model: str = "haiku",
) -> list[SuggestedSkill]:
    """Call Claude to generate suggested skill patterns."""
    import anthropic

    client = anthropic.Anthropic()
    context = build_context_prompt(files, root)

    response = client.messages.create(
        model=MODEL_MAP[model],
        max_tokens=1024,
        tools=[SKILLS_TOOL],  # type: ignore[list-item]
        tool_choice={"type": "tool", "name": "generate_skills"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"{context}\n\nSuggest 2-3 reusable skill patterns for AI coding agents "
                    "working in this repository. Focus on common development tasks."
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_skills":
            skills_data = block.input.get("skills", [])  # type: ignore[union-attr]
            return [
                SuggestedSkill(
                    name=s["name"],
                    description=s["description"],
                    trigger=s["trigger"],
                    steps=s.get("steps", []),
                )
                for s in skills_data
            ]

    return []


# ── Markdown renderers ───────────────────────────────────────────────────────


def architecture_to_markdown(arch: ArchitectureDoc) -> str:
    """Convert ArchitectureDoc to a markdown string."""
    lines = ["# Architecture\n", "## Overview\n", arch.overview, ""]
    lines += ["\n## Key Services\n"]
    for svc in arch.key_services:
        tech = f" ({svc.technology})" if svc.technology else ""
        lines.append(f"- **{svc.name}**{tech}: {svc.description}")
    lines += ["\n## Data Flow\n"]
    for step in arch.data_flow:
        lines.append(f"- {step.source} → {step.sink}: {step.description}")
    lines += ["\n## Dependencies\n"]
    for dep in arch.dependencies:
        lines.append(f"- {dep}")
    return "\n".join(lines)


def conventions_to_markdown(conv: ConventionsDoc) -> str:
    """Convert ConventionsDoc to a markdown string."""
    lines = ["# Conventions\n"]

    def _section(title: str, c: Convention | None) -> None:
        lines.append(f"\n## {title}\n")
        if c:
            lines.append(c.description)
            if c.example:
                lines.append(f"\n```\n{c.example}\n```")
        else:
            lines.append("<!-- Not detected in codebase -->")

    _section("Logging", conv.logging)
    _section("Model Validation", conv.model_validation)
    _section("Test Structure", conv.test_structure)

    if conv.additional:
        lines.append("\n## Additional Conventions\n")
        for c in conv.additional:
            lines.append(f"### {c.name}\n")
            lines.append(c.description)
            if c.example:
                lines.append(f"\n```\n{c.example}\n```")

    return "\n".join(lines)


def skill_to_markdown(skill: SuggestedSkill) -> str:
    """Convert SuggestedSkill to a skill file with frontmatter."""
    lines = [
        "---",
        f"name: {skill.name}",
        f"description: {skill.description}",
        "type: task",
        "---",
        "",
        f"# {skill.name}",
        "",
        f"**Trigger:** {skill.trigger}",
        "",
        "## Steps",
        "",
    ]
    for step in skill.steps:
        lines.append(f"- {step}")
    return "\n".join(lines)
