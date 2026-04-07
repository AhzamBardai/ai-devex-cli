# 002. Structured Output Schema Design

Date: 2026-04-06
Status: Accepted

## Context

`ai-context generate` must produce machine-readable output that:
1. Can be validated without hallucination-prone string parsing
2. Maps cleanly to Pydantic v2 models for downstream use and type safety
3. Supports incremental focus (architecture only, conventions only, skills only)

## Options Considered

**A. Ask Claude for JSON, parse with `json.loads()`, validate with Pydantic**
- Fragile: Claude sometimes wraps JSON in markdown code fences.
- Requires defensive error handling for malformed JSON.

**B. Forced `tool_use` with `tool_choice: {type: tool, name: X}`**
- Guarantees the model returns exactly one tool call.
- The API returns a parsed `input` dict — no string parsing needed.
- Deterministic: same schema, every run.

**C. Claude `response_format` (beta JSON mode)**
- Available but in beta; less stable API.
- Still requires JSON extraction and Pydantic parsing.

## Decision

**Option B** — one forced tool per generation focus:
- `ARCHITECTURE_TOOL` → `ArchitectureDoc`
- `CONVENTIONS_TOOL` → `ConventionsDoc`
- `SKILLS_TOOL` → `list[SuggestedSkill]`

## Rationale

- `tool_choice: {type: tool, name: X}` is the most reliable path to structured output in the Anthropic API as of 2026.
- Pydantic v2 models are the canonical schema; tool input schemas are derived from the same structure.
- Separate tools per focus allow incremental generation without overloading a single prompt.

## Consequences

- Structured output failure raises `ValueError("Claude did not return structured output")` — explicitly testable.
- Adding a new generation focus requires: (1) a new tool schema constant, (2) a new Pydantic model, (3) a new `generate_*` function, (4) a new markdown renderer.
- The `GenerateOutput` model is the contract between `generator.py` and `commands/generate.py`.
