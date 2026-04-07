"""Stats command: report .ai/ context usage statistics."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


def _estimate_tokens(text: str) -> int:
    return len(text) // 4


def run_stats(path: Path = Path(".")) -> dict[str, Any]:
    """Collect statistics about the .ai/ folder.

    Args:
        path: Root directory containing .ai/

    Returns:
        Dictionary with keys: last_updated, memory_files, memory_tokens,
        skills, rules, changelog_sessions, most_used_skill, most_used_skill_count.
    """
    stats: dict[str, Any] = {
        "last_updated": None,
        "memory_files": 0,
        "memory_tokens": 0,
        "skills": 0,
        "rules": 0,
        "changelog_sessions": 0,
        "most_used_skill": None,
        "most_used_skill_count": 0,
    }

    ai_dir = path / ".ai"
    if not ai_dir.exists():
        return stats

    memory_dir = ai_dir / "memory"
    if memory_dir.exists():
        memory_files = [f for f in memory_dir.rglob("*.md") if f.name != "MEMORY.md"]
        stats["memory_files"] = len(memory_files)
        stats["memory_tokens"] = sum(_estimate_tokens(f.read_text()) for f in memory_files)

    skills_dir = ai_dir / "skills"
    if skills_dir.exists():
        stats["skills"] = len(list(skills_dir.rglob("*.md")))

    rules_dir = ai_dir / "rules"
    if rules_dir.exists():
        stats["rules"] = len(
            [f for f in rules_dir.rglob("*.md") if f.stat().st_size > 0]
        )

    all_md = list(ai_dir.rglob("*.md"))
    if all_md:
        latest = max(all_md, key=lambda f: f.stat().st_mtime)
        stats["last_updated"] = datetime.fromtimestamp(
            latest.stat().st_mtime
        ).strftime("%Y-%m-%d")

    changelog = ai_dir / "CHANGELOG.md"
    if changelog.exists():
        content = changelog.read_text()
        sessions = len(re.findall(r"^##\s", content, re.MULTILINE))
        stats["changelog_sessions"] = sessions

        skill_uses: dict[str, int] = {}
        for match in re.finditer(
            r"skill[:\s]+[`\"]?([a-z][a-z0-9-]+)[`\"]?", content, re.IGNORECASE
        ):
            skill = match.group(1).lower()
            skill_uses[skill] = skill_uses.get(skill, 0) + 1
        if skill_uses:
            top = max(skill_uses, key=lambda k: skill_uses[k])
            stats["most_used_skill"] = top
            stats["most_used_skill_count"] = skill_uses[top]

    return stats


def print_stats(data: dict[str, Any], console: Console) -> None:
    """Render statistics to the console."""
    console.print("\n[bold].ai context statistics[/bold]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="dim")
    table.add_column("Value", style="bold")

    last_updated = data.get("last_updated") or "never"
    table.add_row("Last updated", last_updated)
    table.add_row(
        "Memory files",
        f"{data['memory_files']} ({data['memory_tokens']} tokens total)",
    )
    table.add_row("Skills", str(data["skills"]))
    table.add_row("Rules", str(data["rules"]))
    table.add_row("CHANGELOG sessions", str(data["changelog_sessions"]))

    if data.get("most_used_skill"):
        table.add_row(
            "Most used skill",
            f"{data['most_used_skill']} ({data['most_used_skill_count']} uses)",
        )

    console.print(table)
