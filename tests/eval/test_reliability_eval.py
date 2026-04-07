"""Reliability eval: structured output must never fail Pydantic validation across N runs."""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.eval
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_structured_output_never_fails_pydantic() -> None:
    """generate_architecture must never raise on structured output parsing across 5 runs."""
    from ai_context.generator import FileSelector, generate_architecture
    from ai_context.schema import ArchitectureDoc

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    runs = 5
    failures = []
    for i in range(runs):
        try:
            arch = generate_architecture(files, repo, model="haiku")
            assert isinstance(arch, ArchitectureDoc)
        except Exception as e:
            failures.append(f"Run {i + 1}: {e}")

    assert not failures, f"Structured output failed on {len(failures)}/{runs} runs:\n" + "\n".join(
        failures
    )


@pytest.mark.eval
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_section_names_are_stable() -> None:
    """Architecture service names must be recognizably stable across 3 runs."""
    from ai_context.generator import FileSelector, generate_architecture

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    runs = 3
    all_service_words: list[set[str]] = []
    for _ in range(runs):
        arch = generate_architecture(files, repo, model="haiku")
        words: set[str] = set()
        for svc in arch.key_services:
            words.update(svc.name.lower().split())
        all_service_words.append(words)

    # Pairwise overlap: cosine similarity of word sets ≥ 0.40
    for i in range(len(all_service_words)):
        for j in range(i + 1, len(all_service_words)):
            a, b = all_service_words[i], all_service_words[j]
            if not a or not b:
                continue
            intersection = len(a & b)
            cosine = intersection / math.sqrt(len(a) * len(b))
            assert cosine >= 0.40, (
                f"Service name instability between runs {i + 1} and {j + 1}: "
                f"cosine={cosine:.2f}. Run {i + 1}: {a}, Run {j + 1}: {b}"
            )
