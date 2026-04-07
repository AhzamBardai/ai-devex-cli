"""Generate command: AI-powered analysis and context generation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import structlog

from ai_context.generator import (
    FileSelector,
    architecture_to_markdown,
    conventions_to_markdown,
    estimate_tokens,
    generate_architecture,
    generate_conventions,
    generate_skills,
    skill_to_markdown,
)
from ai_context.schema import GenerateOutput

log = structlog.get_logger()


def run_generate(
    path: Path = Path("."),
    model: Literal["haiku", "sonnet"] = "haiku",
    focus: Literal["architecture", "conventions", "skills", "all"] = "all",
    max_tokens: int = 4000,
) -> GenerateOutput:
    """Run AI generation for the .ai/ folder.

    Args:
        path: Root directory of the repository.
        model: LLM model to use ("haiku" for cost, "sonnet" for quality).
        focus: What to generate.
        max_tokens: Maximum token budget for file selection.

    Returns:
        GenerateOutput with generated content.

    Raises:
        EnvironmentError: If ANTHROPIC_API_KEY is not set.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise OSError(
            "ANTHROPIC_API_KEY is not set. Export it or add it to a .env file (never commit .env)."
        )

    selector = FileSelector(path, max_tokens=max_tokens)
    files = selector.select()
    log.info(
        "files_selected",
        count=len(files),
        total_tokens=sum(estimate_tokens(c) for _, c in files),
    )

    output = GenerateOutput()

    if focus in ("architecture", "all"):
        output.architecture = generate_architecture(files, path, model=model)

    if focus in ("conventions", "all"):
        output.conventions = generate_conventions(files, path, model=model)

    if focus in ("skills", "all"):
        output.suggested_skills = generate_skills(files, path, model=model)

    return output


def write_output(output: GenerateOutput, path: Path) -> list[str]:
    """Write GenerateOutput to .ai/ folder.

    Args:
        output: Generated content from Claude.
        path: Repository root.

    Returns:
        List of relative file paths that were written.
    """
    ai_dir = path / ".ai"
    written: list[str] = []

    if output.architecture:
        arch_file = ai_dir / "memory" / "architecture.md"
        arch_file.parent.mkdir(parents=True, exist_ok=True)
        arch_file.write_text(architecture_to_markdown(output.architecture))
        written.append(str(arch_file.relative_to(path)))

    if output.conventions:
        conv_file = ai_dir / "memory" / "conventions.md"
        conv_file.parent.mkdir(parents=True, exist_ok=True)
        conv_file.write_text(conventions_to_markdown(output.conventions))
        written.append(str(conv_file.relative_to(path)))

    if output.suggested_skills:
        skills_dir = ai_dir / "skills" / "suggested"
        skills_dir.mkdir(parents=True, exist_ok=True)
        for skill in output.suggested_skills:
            safe_name = skill.name.lower().replace(" ", "-").replace("/", "-")
            skill_file = skills_dir / f"{safe_name}.md"
            skill_file.write_text(skill_to_markdown(skill))
            written.append(str(skill_file.relative_to(path)))

    return written
