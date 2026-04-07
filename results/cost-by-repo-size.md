# Cost by Repo Size

Token consumption and estimated cost (claude-haiku-4-5-20251001) per `ai-context generate` call.

| Tier   | Fixture          | Input Tokens | Output Tokens | Cost (USD) | Target   |
|--------|-----------------|--------------|---------------|------------|----------|
| small  | minimal_project | ~200         | ~300          | ~$0.0004   | —        |
| medium | python_kafka    | ~1,500       | ~600          | ~$0.0011   | < $0.01  |
| large  | mixed_monorepo  | ~3,500       | ~800          | ~$0.0019   | —        |

*Estimates based on fixture repo sizes. Update with actual measured values after running `make eval`.*

## Notes

- Token budget capped at 4,000 tokens via `--max-tokens` (default).
- Haiku pricing: $0.25/1M input, $1.25/1M output tokens.
- Sonnet is ~10x more expensive per token; use `--model sonnet` only for quality-critical generation.
- Run `pytest tests/eval/test_cost_eval.py -v -m eval` to measure actual costs.
