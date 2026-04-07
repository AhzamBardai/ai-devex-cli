"""Cost eval: measure tokens consumed per repo size tier."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"

REPO_TIERS = {
    "small": "minimal_project",
    "medium": "python_kafka",
    "large": "mixed_monorepo",
}

# Haiku pricing: $0.25/1M input, $1.25/1M output
HAIKU_INPUT_COST_PER_TOKEN = 0.00000025
HAIKU_OUTPUT_COST_PER_TOKEN = 0.00000125


@pytest.mark.eval
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
@pytest.mark.parametrize("tier,fixture_name", list(REPO_TIERS.items()))
def test_cost_per_tier(tier: str, fixture_name: str) -> None:
    """Medium repo must cost < $0.01 per generate call on haiku."""
    import anthropic

    from ai_context.generator import (
        ARCHITECTURE_TOOL,
        MODEL_MAP,
        FileSelector,
        build_context_prompt,
    )

    repo = FIXTURES / fixture_name
    if not repo.exists():
        pytest.skip(f"Fixture {fixture_name} not found")

    selector = FileSelector(repo, max_tokens=4000)
    files = selector.select()
    context = build_context_prompt(files, repo)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL_MAP["haiku"],
        max_tokens=2048,
        tools=[ARCHITECTURE_TOOL],  # type: ignore[list-item]
        tool_choice={"type": "tool", "name": "generate_architecture"},
        messages=[
            {
                "role": "user",
                "content": context + "\n\nGenerate architecture documentation.",
            }
        ],
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (input_tokens * HAIKU_INPUT_COST_PER_TOKEN) + (
        output_tokens * HAIKU_OUTPUT_COST_PER_TOKEN
    )

    print(
        f"\n[{tier}] {fixture_name}: input={input_tokens}, output={output_tokens}, cost=${cost:.6f}"
    )

    if tier == "medium":
        assert cost < 0.01, f"Medium repo cost ${cost:.6f} exceeds $0.01 target"
