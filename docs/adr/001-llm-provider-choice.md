# 001. LLM Provider Choice

Date: 2026-04-06
Status: Accepted

## Context

The `generate` command needs an LLM to analyze codebases and produce structured documentation. The main options considered:

1. **Anthropic Claude** via the `anthropic` SDK
2. **OpenAI GPT-4** via the `openai` SDK
3. **Local models** via Ollama or LM Studio

## Decision

Use **Anthropic Claude** with two tiers:

- `claude-haiku-4-5-20251001` as the default (low cost, fast, adequate quality)
- `claude-sonnet-4-6` as the quality option (`--model sonnet`)

## Rationale

1. **Forced structured output**: Claude's `tool_use` API with `tool_choice: {type: tool, name: X}` guarantees the model returns exactly one tool call with a validated schema. No JSON extraction heuristics.

2. **Cost**: Haiku costs ~$0.001 per medium repo analysis, well within the < $0.01 target. OpenAI GPT-4 is 10–30x more expensive for equivalent quality.

3. **Simplicity**: A single SDK dependency. No provider abstraction layer needed at this scale.

4. **Quality**: Claude's instruction-following on code analysis is strong — it correctly identifies Kafka consumers, Elasticsearch sinks, and Pydantic model patterns from file content alone.

## Consequences

- `ANTHROPIC_API_KEY` is required for `generate`. The command fails fast with a clear error if missing.
- All other commands (init, validate, diff, stats) work without any API key.
- If a user wants a different provider, they can replace `generate_architecture()` and `generate_conventions()` in `ai_context/generator.py` with any compatible implementation.
