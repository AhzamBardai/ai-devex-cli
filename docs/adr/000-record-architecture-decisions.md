# 000. Record Architecture Decisions

Date: 2026-04-06
Status: Accepted

## Context

We need a way to record the architectural decisions made during the development of `ai-context`. Decisions are hard to reconstruct from code alone and are frequently asked about by contributors.

## Decision

We will use Architecture Decision Records (ADRs), as described by Michael Nygard. Each ADR is a short Markdown document in `docs/adr/`.

## Consequences

- Architectural decisions are documented, discoverable, and easy to reason about.
- Future contributors can understand why things are the way they are, not just what they are.
- ADRs are immutable — we add new ones rather than modifying old ones.
