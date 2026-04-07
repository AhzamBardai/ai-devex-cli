"""Unit tests for generate command internals and markdown renderers."""

from pathlib import Path
from unittest.mock import patch

import pytest

from ai_context.schema import (
    ArchitectureDoc,
    Convention,
    ConventionsDoc,
    DataFlowStep,
    KeyService,
    SuggestedSkill,
)

# ── Markdown renderers ────────────────────────────────────────────────────────


def test_architecture_to_markdown_sections() -> None:
    from ai_context.generator import architecture_to_markdown

    arch = ArchitectureDoc(
        overview="A system overview.",
        key_services=[KeyService(name="Consumer", description="Reads events", technology="Python")],
        data_flow=[DataFlowStep(source="Kafka", sink="Elasticsearch", description="streams data")],
        dependencies=["kafka-python", "elasticsearch-py"],
    )
    md = architecture_to_markdown(arch)
    assert "## Overview" in md
    assert "## Key Services" in md
    assert "## Data Flow" in md
    assert "## Dependencies" in md
    assert "Consumer" in md
    assert "kafka-python" in md
    assert "Kafka → Elasticsearch" in md


def test_conventions_to_markdown_sections() -> None:
    from ai_context.generator import conventions_to_markdown

    conv = ConventionsDoc(
        logging=Convention(name="structlog", description="Uses structlog for JSON logging"),
        model_validation=Convention(name="pydantic", description="Uses Pydantic v2"),
        test_structure=Convention(name="pytest", description="Uses pytest with tmp_path"),
    )
    md = conventions_to_markdown(conv)
    assert "## Logging" in md
    assert "## Model Validation" in md
    assert "## Test Structure" in md
    assert "structlog" in md
    assert "Pydantic" in md or "pydantic" in md


def test_conventions_to_markdown_none_sections() -> None:
    from ai_context.generator import conventions_to_markdown

    conv = ConventionsDoc()
    md = conventions_to_markdown(conv)
    assert "## Logging" in md
    assert "Not detected" in md


def test_conventions_to_markdown_additional() -> None:
    from ai_context.generator import conventions_to_markdown

    conv = ConventionsDoc(
        additional=[Convention(name="Error Handling", description="Uses custom exception classes")]
    )
    md = conventions_to_markdown(conv)
    assert "Additional Conventions" in md
    assert "Error Handling" in md


def test_skill_to_markdown_has_frontmatter() -> None:
    from ai_context.generator import skill_to_markdown

    skill = SuggestedSkill(
        name="run-tests",
        description="Run the test suite",
        trigger="When asked to run tests",
        steps=["Run pytest", "Check coverage"],
    )
    md = skill_to_markdown(skill)
    assert md.startswith("---")
    assert "name: run-tests" in md
    assert "description: Run the test suite" in md
    assert "Run pytest" in md


# ── write_output ─────────────────────────────────────────────────────────────


def test_write_output_creates_architecture_file(tmp_path: Path) -> None:
    from ai_context.commands.generate import write_output
    from ai_context.schema import GenerateOutput

    output = GenerateOutput(
        architecture=ArchitectureDoc(
            overview="Test overview",
            key_services=[],
            data_flow=[],
            dependencies=[],
        )
    )
    written = write_output(output, tmp_path)
    assert any("architecture.md" in w for w in written)
    assert (tmp_path / ".ai" / "memory" / "architecture.md").exists()


def test_write_output_creates_conventions_file(tmp_path: Path) -> None:
    from ai_context.commands.generate import write_output
    from ai_context.schema import GenerateOutput

    output = GenerateOutput(
        conventions=ConventionsDoc(logging=Convention(name="structlog", description="JSON logging"))
    )
    written = write_output(output, tmp_path)
    assert any("conventions.md" in w for w in written)


def test_write_output_creates_skill_files(tmp_path: Path) -> None:
    from ai_context.commands.generate import write_output
    from ai_context.schema import GenerateOutput

    output = GenerateOutput(
        suggested_skills=[
            SuggestedSkill(name="commit", description="Commit changes", trigger="on commit")
        ]
    )
    written = write_output(output, tmp_path)
    assert any("commit.md" in w for w in written)


# ── run_generate ──────────────────────────────────────────────────────────────


def test_run_generate_raises_without_api_key(tmp_path: Path) -> None:
    import os

    from ai_context.commands.generate import run_generate

    with patch.dict("os.environ", {}, clear=True):
        if "ANTHROPIC_API_KEY" in os.environ:
            pass  # can't test without clearing
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(OSError, match="ANTHROPIC_API_KEY"):
                run_generate(path=tmp_path)


# ── diff print ────────────────────────────────────────────────────────────────


def test_print_diff_no_changes(capsys: pytest.CaptureFixture) -> None:
    from rich.console import Console

    from ai_context.commands.diff import print_diff
    from ai_context.schema import DiffResult

    console = Console()
    result = DiffResult()
    print_diff(result, console)
    captured = capsys.readouterr()
    assert "No changes" in captured.out


def test_print_diff_with_stale_hint(capsys: pytest.CaptureFixture) -> None:
    from rich.console import Console

    from ai_context.commands.diff import print_diff
    from ai_context.schema import DiffResult, StaleHint

    console = Console()
    result = DiffResult(
        stale_hints=[
            StaleHint(
                new_file="notifier.py",
                message="architecture.md may be stale — new file notifier.py not reflected",
                suggestion="Run ai-context generate",
            )
        ]
    )
    print_diff(result, console)
    captured = capsys.readouterr()
    assert "notifier.py" in captured.out


# ── stats print ───────────────────────────────────────────────────────────────


def test_print_stats_with_most_used_skill(capsys: pytest.CaptureFixture) -> None:
    from rich.console import Console

    from ai_context.commands.stats import print_stats

    console = Console()
    data = {
        "last_updated": "2026-04-06",
        "memory_files": 3,
        "memory_tokens": 500,
        "skills": 4,
        "rules": 1,
        "changelog_sessions": 10,
        "most_used_skill": "commit",
        "most_used_skill_count": 5,
    }
    print_stats(data, console)
    captured = capsys.readouterr()
    assert "commit" in captured.out
    assert "Memory files" in captured.out
