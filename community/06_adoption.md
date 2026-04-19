# Adoption

Adoption is a product outcome, not just a distribution outcome.

## Minimal Viable Utility (MVU)

- Solve one painful friction first (your own workflow pain is the best seed).
- Keep a zero-config path and enforce the 5-minute rule for first success.
- Ship one visible utility before broad platform features.

## Adoption loop

1. Install and run one working example in under 5 minutes.
2. Integrate parse + match into one real workflow.
3. Add one custom plugin (model adapter, data connector, or ranking strategy).
4. Measure match quality and latency.
5. Roll out to production with guardrails and confidence thresholds.

## Documentation as product

- First two scrolls of `README.md` should show: Problem -> Solution -> Quick Start.
- Add a demo GIF or terminal recording for instant trust.
- Keep examples runnable copy-paste blocks, not pseudocode.

## High-velocity governance

- Tag approachable tasks with `good-first-issue`.
- Acknowledge issues and pull requests within 24-48 hours.
- Treat responsiveness as a core maintainer SLA.

## Ecosystem integration and sustainability

- Integrate cleanly with MCP/Skill runtimes, CI, and provider SDK standards.
- Prefer modular maintainership over single-person gatekeeping.
- Keep the core small; let plugins carry ecosystem-specific complexity.

## Suggested rollout metrics

- Time to first successful match
- Top-k precision of ranked matches
- Clarification loop completion rate
- Latency and estimated model cost per request
