"""Unit tests for the stats command."""

from pathlib import Path

import pytest


def _scaffold(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)


def test_stats_empty_dir_returns_defaults(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    data = run_stats(tmp_path)
    assert data["memory_files"] == 0
    assert data["skills"] == 0
    assert data["rules"] == 0


def test_stats_counts_memory_files(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    (tmp_path / ".ai" / "memory" / "architecture.md").write_text("# Arch\n")
    (tmp_path / ".ai" / "memory" / "conventions.md").write_text("# Conv\n")
    data = run_stats(tmp_path)
    assert data["memory_files"] == 2


def test_stats_counts_skills(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    (tmp_path / ".ai" / "skills" / "skill1.md").write_text("# Skill 1\n")
    (tmp_path / ".ai" / "skills" / "skill2.md").write_text("# Skill 2\n")
    data = run_stats(tmp_path)
    assert data["skills"] == 2


def test_stats_counts_rules(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    (tmp_path / ".ai" / "rules" / "coding-standards.md").write_text("# Standards\n" * 5)
    data = run_stats(tmp_path)
    assert data["rules"] == 1


def test_stats_estimates_tokens(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    (tmp_path / ".ai" / "memory" / "arch.md").write_text("x" * 400)  # ~100 tokens
    data = run_stats(tmp_path)
    assert data["memory_tokens"] == pytest.approx(100, abs=5)


def test_stats_changelog_sessions(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    changelog = tmp_path / ".ai" / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## Session 2026-04-01\nDid stuff.\n\n## Session 2026-04-02\nDid more.\n"
    )
    data = run_stats(tmp_path)
    assert data["changelog_sessions"] == 2


def test_stats_reports_last_updated(tmp_path: Path) -> None:
    from ai_context.commands.stats import run_stats

    _scaffold(tmp_path)
    (tmp_path / ".ai" / "memory" / "arch.md").write_text("# Arch\n")
    data = run_stats(tmp_path)
    assert data["last_updated"] is not None
    assert len(data["last_updated"]) == 10  # YYYY-MM-DD
