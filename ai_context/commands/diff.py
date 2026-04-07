"""Diff command: compare .ai/ against git HEAD and detect stale context."""

from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console

from ai_context.schema import DiffEntry, DiffResult, StaleHint


def _run_git(args: list[str], cwd: Path) -> str | None:
    """Run a git command and return stdout, or None on any failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except FileNotFoundError:
        return None


def _parse_git_diff(diff_text: str) -> list[DiffEntry]:
    """Parse unified diff output into DiffEntry objects."""
    entries: list[DiffEntry] = []
    current_file: str | None = None
    additions: list[str] = []
    removals: list[str] = []

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            if current_file:
                entries.append(DiffEntry(file=current_file, additions=additions, removals=removals))
            current_file = line[6:]
            additions = []
            removals = []
        elif line.startswith("+") and not line.startswith("+++"):
            stripped = line[1:].strip()
            if stripped:
                additions.append(stripped)
        elif line.startswith("-") and not line.startswith("---"):
            stripped = line[1:].strip()
            if stripped:
                removals.append(stripped)

    if current_file:
        entries.append(DiffEntry(file=current_file, additions=additions, removals=removals))

    return entries


def run_diff(path: Path = Path(".")) -> DiffResult:
    """Compare .ai/ against git HEAD and detect stale context.

    Args:
        path: Root directory of the repository.

    Returns:
        DiffResult with changed entries and stale hints.
    """
    result = DiffResult()
    ai_dir = path / ".ai"

    if not ai_dir.exists():
        return result

    diff_text = _run_git(["diff", "HEAD", "--", ".ai/"], path)
    if diff_text is None:
        return result

    if diff_text:
        result.entries = _parse_git_diff(diff_text)

    arch_file = ai_dir / "memory" / "architecture.md"
    if arch_file.exists():
        arch_content = arch_file.read_text().lower()
        new_files_output = _run_git(["diff", "--name-status", "HEAD"], path)

        if new_files_output:
            for line in new_files_output.splitlines():
                if not line.startswith(("A\t", "A ")):
                    continue
                new_file = line.split("\t", 1)[-1].strip()
                if not new_file.endswith((".py", ".ts", ".tsx", ".kt", ".java", ".go", ".rs")):
                    continue
                stem = Path(new_file).stem.lower()
                if stem not in arch_content:
                    result.stale_hints.append(
                        StaleHint(
                            new_file=new_file,
                            message=(
                                f".ai/memory/architecture.md may be stale — "
                                f"new file {new_file} not reflected"
                            ),
                            suggestion=("Run `ai-context generate --focus architecture` to update"),
                        )
                    )

    return result


def print_diff(result: DiffResult, console: Console) -> None:
    """Render DiffResult to the console."""
    if not result.has_changes:
        console.print("[green]✓[/green] No changes to .ai/ context since last commit.")
        return

    for entry in result.entries:
        console.print(f"\n[bold]{entry.file}[/bold]")
        for line in entry.additions[:5]:
            console.print(f"  [green]+[/green] Added: {line[:80]}")
        for line in entry.removals[:5]:
            console.print(f"  [red]-[/red] Removed: {line[:80]}")

    for hint in result.stale_hints:
        console.print(f"\n[yellow]⚠[/yellow] {hint.message}")
        console.print(f"  [dim]→ {hint.suggestion}[/dim]")
