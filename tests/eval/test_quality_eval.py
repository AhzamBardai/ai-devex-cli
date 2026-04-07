"""Quality eval: section completeness and service recall across 5 fixture repos."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"

FIXTURE_GROUND_TRUTH: dict[str, dict] = {
    "python_kafka": {
        "must_contain": ["kafka", "elasticsearch"],
        "known_services": ["consumer", "enricher", "sink", "kafka", "elasticsearch"],
    },
    "kotlin_service": {
        "must_contain": ["stripe", "payment"],
        "known_services": ["payment", "stripe", "repository"],
    },
    "typescript_app": {
        "must_contain": ["firebase", "notification"],
        "known_services": ["notification", "firebase", "sendgrid"],
    },
    "mixed_monorepo": {
        "must_contain": ["fastapi", "next"],
        "known_services": ["api", "web", "postgres", "redis"],
    },
    "minimal_project": {
        "must_contain": ["cli"],
        "known_services": [],
    },
}


@pytest.mark.eval
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
@pytest.mark.parametrize("fixture_name", list(FIXTURE_GROUND_TRUTH.keys()))
def test_architecture_section_completeness(fixture_name: str) -> None:
    """Each fixture must produce architecture with ≥ 3/4 sections populated."""
    from ai_context.generator import FileSelector, generate_architecture

    repo = FIXTURES / fixture_name
    if not repo.exists():
        pytest.skip(f"Fixture {fixture_name} not found")

    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()
    arch = generate_architecture(files, repo, model="haiku")

    score = sum(
        [
            bool(arch.overview and len(arch.overview) > 20),
            bool(arch.key_services),
            bool(arch.data_flow),
            bool(arch.dependencies),
        ]
    )

    assert score >= 3, (
        f"[{fixture_name}] Section completeness {score}/4, expected ≥ 3. "
        f"services={len(arch.key_services)}, flow={len(arch.data_flow)}, "
        f"deps={len(arch.dependencies)}"
    )


@pytest.mark.eval
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
@pytest.mark.parametrize(
    "fixture_name",
    [k for k, v in FIXTURE_GROUND_TRUTH.items() if v["known_services"]],
)
def test_service_recall(fixture_name: str) -> None:
    """Key services must appear in generated architecture (recall ≥ 0.80)."""
    from ai_context.generator import FileSelector, generate_architecture

    repo = FIXTURES / fixture_name
    truth = FIXTURE_GROUND_TRUTH[fixture_name]
    known = truth["known_services"]

    selector = FileSelector(repo, max_tokens=3000)
    files = selector.select()
    arch = generate_architecture(files, repo, model="haiku")

    all_text = (
        arch.overview + " ".join(s.name + " " + s.description for s in arch.key_services)
    ).lower()

    hits = sum(1 for svc in known if svc.lower() in all_text)
    recall = hits / len(known) if known else 1.0

    assert recall >= 0.80, (
        f"[{fixture_name}] Service recall {recall:.2f}, expected ≥ 0.80. "
        f"Known: {known}. Generated: {[s.name for s in arch.key_services]}"
    )
