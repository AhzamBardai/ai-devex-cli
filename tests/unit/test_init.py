"""Unit tests for the init command."""
import time
import tomllib
from pathlib import Path


def test_init_creates_all_expected_files(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    created = run_init(path=tmp_path)
    assert (tmp_path / ".ai" / "memory" / "MEMORY.md").exists()
    assert (tmp_path / ".ai" / "rules" / ".gitkeep").exists()
    assert (tmp_path / ".ai" / "skills" / ".gitkeep").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "ai-context.toml").exists()
    assert len(created) == 5


def test_init_is_idempotent(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)
    created_second = run_init(path=tmp_path)
    assert len(created_second) == 0


def test_init_no_agents_md(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path, no_agents_md=True)
    assert not (tmp_path / "AGENTS.md").exists()


def test_init_full_template_creates_memory_files(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(template="full", path=tmp_path)
    assert (tmp_path / ".ai" / "memory" / "architecture.md").exists()
    assert (tmp_path / ".ai" / "memory" / "conventions.md").exists()


def test_init_team_template_creates_team_standards(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(template="team", path=tmp_path)
    assert (tmp_path / ".ai" / "rules" / "team-standards.md").exists()


def test_init_latency_under_100ms(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    start = time.perf_counter()
    run_init(path=tmp_path)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 100, f"init took {elapsed_ms:.1f}ms, expected < 100ms"


def test_init_memory_md_has_expected_content(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)
    content = (tmp_path / ".ai" / "memory" / "MEMORY.md").read_text()
    assert "# Memory" in content


def test_init_agents_md_references_ai_folder(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert ".ai/" in content


def test_init_toml_is_valid_toml(tmp_path: Path) -> None:
    from ai_context.commands.init import run_init

    run_init(path=tmp_path)
    content = (tmp_path / "ai-context.toml").read_bytes()
    parsed = tomllib.loads(content.decode())
    assert "project" in parsed
