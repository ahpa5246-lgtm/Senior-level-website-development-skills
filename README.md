# Senior-level website development framework

A practical decision and verification framework for AI-assisted engineering. Quality means complete user outcomes, protected data, measured performance, understandable code, and recoverable operations. File count, visual polish, and architectural complexity are not evidence of quality.

## Start here

1. Read [AGENTS.md](AGENTS.md) and [the delivery workflow](docs/01-delivery-workflow.md).
2. Complete [the project brief](templates/project-brief.md), [feature contract](templates/feature-contract.md), and [design brief](templates/design-brief.md).
3. Select an architecture using [architecture and data](docs/02-architecture-and-data.md), then apply [security](docs/03-security-and-api.md) and [design](docs/04-design-and-accessibility.md).
4. Set [resource budgets](docs/05-performance-and-operations.md) before adding effects or dependencies.
5. Review all applicable entries in [the 100-error matrix](docs/100-error-matrix.md). Each has a constructive alternative and an observable check.
6. Deliver [release evidence](templates/release-evidence.md), not a claim that the site “looks finished.”

## What this repository contains

| Resource | Purpose |
| --- | --- |
| [Book analysis](docs/book-insights.md) | Source-specific lessons, trade-offs, and limitations |
| [Sources](docs/sources.md) | Verified references and attribution boundaries |
| [AI prompt](prompts/build-and-review.md) | A staged operating prompt with explicit stop conditions |
| [Architecture decision](templates/architecture-decision.md) | Context, alternatives, consequences, revisit trigger |
| [Worked example](docs/06-worked-example.md) | Complete reservation flow across UI, API, data, failures, and tests |
| [Validation script](scripts/validate.py) | Matrix coverage and local documentation integrity |

## Principles

- Choose the smallest architecture that satisfies explicit user outcomes and risk constraints.
- A static informational site may legitimately need no backend. Persistent accounts, orders, permissions, shared data, or paid transactions require real trusted server-side behavior. A single HTML prototype is not a completed transactional product.
- Every displayed control must implement its promised behavior or clearly communicate an unavailable feature. Never silently simulate success.
- Treat generated code as untrusted until reviewed and exercised. Never claim “secure,” “production ready,” or “fast” without scoped evidence.
- Use positive design direction: audience, content, hierarchy, interaction patterns, typography, semantic color, and resource cost. No blanket ban on purple, cards, gradients, or any particular font.
- Apply rules conditionally. An N/A decision requires a reason. A failed security or data-integrity gate cannot be averaged away by a good overall score.

These are engineering instructions, not model training: supplying the repository can guide an AI in the current context; it does not permanently retrain it or guarantee flawless output.

## Provenance and scope

Original synthesis based on targeted reading of four supplied books and visual inspection of eight supplied architecture summary images, supplemented by official web documentation checked on 2026-10-14. This is not a claim of exhaustive cover-to-cover analysis. No copyrighted book files, extracted chapters, or screenshots are redistributed here. See the source ledger for edition details and locations.

Documentation is in English for broad AI/tool compatibility; [Arabic quick start](docs/arabic-quick-start.md) explains how to use it.

Run `python3 scripts/validate.py` from the repository root. This validates the documentation, not the security or performance of an application built with it.
