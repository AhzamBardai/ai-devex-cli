"""Integration tests: haiku vs sonnet quality comparison."""
import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_haiku_produces_valid_pydantic_output() -> None:
    from ai_context.generator import FileSelector, generate_architecture
    from ai_context.schema import ArchitectureDoc

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    arch = generate_architecture(files, repo, model="haiku")
    assert isinstance(arch, ArchitectureDoc)
    assert arch.overview


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
def test_sonnet_service_count_at_least_as_good_as_haiku() -> None:
    """Sonnet should produce at least as many services as haiku."""
    from ai_context.generator import FileSelector, generate_architecture

    repo = FIXTURES / "python_kafka"
    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()

    haiku_arch = generate_architecture(files, repo, model="haiku")
    sonnet_arch = generate_architecture(files, repo, model="sonnet")

    assert isinstance(haiku_arch.key_services, list)
    assert isinstance(sonnet_arch.key_services, list)
    # Sonnet should not produce fewer services than haiku
    assert len(sonnet_arch.key_services) >= len(haiku_arch.key_services)
