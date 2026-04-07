"""Integration tests: run generate on fixture repos against the real Claude API."""
import os
import shutil
import time
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_generate_architecture_python_kafka() -> None:
    from ai_context.generator import FileSelector, generate_architecture
    from ai_context.schema import ArchitectureDoc

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()
    assert len(files) > 0

    arch = generate_architecture(files, repo, model="haiku")

    assert isinstance(arch, ArchitectureDoc)
    assert len(arch.overview) > 50
    assert len(arch.key_services) >= 1
    assert len(arch.dependencies) >= 1

    all_text = (
        arch.overview
        + " ".join(s.name + " " + s.description for s in arch.key_services)
        + " ".join(arch.dependencies)
    ).lower()
    assert "kafka" in all_text, f"Expected 'kafka' in generated output. Got: {all_text[:500]}"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_generate_architecture_has_at_least_3_sections() -> None:
    from ai_context.generator import FileSelector, generate_architecture

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    arch = generate_architecture(files, repo, model="haiku")

    sections_populated = sum(
        [
            bool(arch.overview),
            bool(arch.key_services),
            bool(arch.data_flow),
            bool(arch.dependencies),
        ]
    )
    assert sections_populated >= 3, f"Expected ≥3 sections, got {sections_populated}"


@pytest.mark.integration
@pytest.mark.use_case
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_use_case_1_scaffold_and_generate(tmp_path: Path) -> None:
    """Use Case 1: scaffold + generate for a Python microservice repo (< 30s, < 100ms init)."""
    from ai_context.commands.generate import run_generate, write_output
    from ai_context.commands.init import run_init
    from ai_context.validator import validate_ai_folder

    dest = tmp_path / "python_kafka"
    shutil.copytree(FIXTURES / "python_kafka", dest)

    # init must be < 100ms
    start = time.perf_counter()
    run_init(path=dest)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 100, f"init took {elapsed_ms:.1f}ms, expected < 100ms"

    assert (dest / ".ai" / "memory" / "MEMORY.md").exists()
    assert (dest / "AGENTS.md").exists()

    # generate architecture < 30s
    start = time.perf_counter()
    output = run_generate(path=dest, model="haiku", focus="architecture", max_tokens=3000)
    elapsed_s = time.perf_counter() - start
    assert elapsed_s < 30, f"generate took {elapsed_s:.1f}s, expected < 30s"

    written = write_output(output, dest)
    assert any("architecture.md" in w for w in written)

    arch_content = (dest / ".ai" / "memory" / "architecture.md").read_text().lower()
    assert "kafka" in arch_content, "architecture.md must mention Kafka"

    # generate conventions
    output2 = run_generate(path=dest, model="haiku", focus="conventions", max_tokens=3000)
    write_output(output2, dest)

    conv_content = (dest / ".ai" / "memory" / "conventions.md").read_text().lower()
    assert "pydantic" in conv_content or "structlog" in conv_content

    # validate passes
    result = validate_ai_folder(dest)
    assert result.passed, f"Validation failed: {result.errors}"
