"""Convention linter for the .ai/ folder structure."""

from __future__ import annotations

import re
from pathlib import Path

from ai_context.schema import ValidationIssue, ValidationResult

REQUIRED_SKILL_FRONTMATTER = {"name", "description"}
REQUIRED_ARCHITECTURE_SECTIONS = {
    "## overview",
    "## key services",
    "## data flow",
    "## dependencies",
}


def validate_ai_folder(path: Path = Path(".")) -> ValidationResult:
    """Lint the .ai/ folder against the convention schema.

    Args:
        path: Root directory containing .ai/

    Returns:
        ValidationResult with any errors or warnings found.
    """
    result = ValidationResult()
    ai_dir = path / ".ai"

    if not ai_dir.exists():
        result.errors.append(
            ValidationIssue(
                file=".ai/",
                message=".ai/ folder does not exist",
                suggestion="Run `ai-context init` to scaffold the folder structure",
            )
        )
        return result

    memory_md = ai_dir / "memory" / "MEMORY.md"
    if not memory_md.exists():
        result.errors.append(
            ValidationIssue(
                file=".ai/memory/MEMORY.md",
                message="MEMORY.md index file is missing",
                suggestion="Run `ai-context init` to create it",
            )
        )
    else:
        _validate_memory_index(memory_md, ai_dir / "memory", result)

    skills_dir = ai_dir / "skills"
    if skills_dir.exists():
        for skill_file in skills_dir.rglob("*.md"):
            _validate_skill_frontmatter(skill_file, path, result)

    arch_file = ai_dir / "memory" / "architecture.md"
    if arch_file.exists():
        _validate_architecture_sections(arch_file, path, result)

    return result


def _validate_memory_index(
    memory_md: Path,
    memory_dir: Path,
    result: ValidationResult,
) -> None:
    content = memory_md.read_text()
    # Strip HTML comments before scanning links to avoid false positives from example comments
    content_stripped = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content_stripped)
    for title, href in links:
        if href.startswith("http"):
            continue
        target = memory_dir / href
        if not target.exists():
            result.errors.append(
                ValidationIssue(
                    file=".ai/memory/MEMORY.md",
                    message=f"Link target does not exist: {href} (referenced as '{title}')",
                    suggestion=f"Create .ai/memory/{href} or remove the link from MEMORY.md",
                )
            )


def _validate_skill_frontmatter(
    skill_file: Path,
    root: Path,
    result: ValidationResult,
) -> None:
    content = skill_file.read_text()
    rel = str(skill_file.relative_to(root))

    if not content.startswith("---"):
        result.errors.append(
            ValidationIssue(
                file=rel,
                message="Skill file is missing YAML frontmatter",
                suggestion="Add frontmatter block starting with --- including name and description",
            )
        )
        return

    end = content.find("---", 3)
    if end == -1:
        result.errors.append(
            ValidationIssue(
                file=rel,
                message="Skill file has malformed frontmatter (missing closing ---)",
                suggestion="Add a closing --- to complete the frontmatter block",
            )
        )
        return

    frontmatter = content[3:end]
    missing = sorted(
        field
        for field in REQUIRED_SKILL_FRONTMATTER
        if not re.search(rf"^{field}:", frontmatter, re.MULTILINE)
    )
    if missing:
        result.errors.append(
            ValidationIssue(
                file=rel,
                message=f"Skill file missing required frontmatter fields: {', '.join(missing)}",
                suggestion=f"Add the missing fields: {', '.join(missing)}",
            )
        )


def _validate_architecture_sections(
    arch_file: Path,
    root: Path,
    result: ValidationResult,
) -> None:
    content = arch_file.read_text()
    rel = str(arch_file.relative_to(root))
    content_lower = content.lower()

    display_names = {
        "## overview": "## Overview",
        "## key services": "## Key Services",
        "## data flow": "## Data Flow",
        "## dependencies": "## Dependencies",
    }

    for section_lower, section_display in display_names.items():
        if section_lower not in content_lower:
            result.errors.append(
                ValidationIssue(
                    file=rel,
                    message=f"Missing required section: '{section_display}'",
                    suggestion=(
                        f"Add a '{section_display}' section or run "
                        "`ai-context generate --focus architecture` to regenerate"
                    ),
                )
            )
