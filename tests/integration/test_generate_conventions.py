"""Integration tests: convention generation quality checks."""
import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_conventions_mentions_known_libraries() -> None:
    """Must detect at least 2 of 4 known conventions in python_kafka fixture."""
    from ai_context.generator import FileSelector, generate_conventions

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    conv = generate_conventions(files, repo, model="haiku")

    known = ["pydantic", "structlog", "pytest", "kafka"]
    all_text = " ".join(
        filter(
            None,
            [
                conv.logging.description if conv.logging else "",
                conv.model_validation.description if conv.model_validation else "",
                conv.test_structure.description if conv.test_structure else "",
            ]
            + [c.description for c in conv.additional],
        )
    ).lower()

    matches = sum(1 for lib in known if lib in all_text)
    assert matches >= 2, (
        f"Expected ≥2 known libs in conventions, got {matches}. Text: {all_text[:500]}"
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_conventions_is_valid_pydantic_model() -> None:
    from ai_context.generator import FileSelector, generate_conventions
    from ai_context.schema import ConventionsDoc

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    conv = generate_conventions(files, repo, model="haiku")
    assert isinstance(conv, ConventionsDoc)
