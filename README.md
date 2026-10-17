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

## Guided projects for non-programmers (new)

Start with the [skeptical project conductor](prompts/skeptical-conductor.md) and its [portfolio operating model](docs/portfolio-operating-model.md). The interview uses [20 simple questions](config/20-questions-ar.json) and can stop before any paid/unsafe architecture choice. Use the **full [500 paired mistakes and senior remedies](docs/500-senior-pairs-ar.md)** alongside the original [100 evidence-oriented checks](docs/100-error-matrix.md). The paired 500 are conditional editorial guidance, not 500 mandatory tests.

A real zero-dependency [intake verifier](scripts/portfolio_intake.py) checks incomplete answers, declared budgets and quotes, reference-repository licensing flags and reviewer/task-packet structure. Example: `python3 scripts/portfolio_intake.py assess --input examples/zero-budget-demo.intake.json`. A separate `packet` command requires linked reviewer evidence and a concrete task plan before emitting a supervisor handoff. **Passing the verifier does not certify provider rates, evidence truthfulness, design quality or production readiness.**

The private [autonomous-project-manager](https://github.com/ahpa5246-lgtm/autonomous-project-manager) remains the project-portfolio supervisor; this public repo does not run Codex continuously, charge services or merge PRs. Keep real project briefs and budgets private.

### Verified repository discovery (new)
Use the [bounded public GitHub researcher](scripts/github_reference_research.py) to produce a JSON shortlist with repository URL, exact current commit, checked license endpoint, top-level test/deploy indicators and explicit unverified costs/security:
```bash
python3 scripts/github_reference_research.py --query "event registration management" --limit 2 --out local-reference-report.json --live
```
The live request requires explicit `--live`, never clones/runs source code and marks every candidate for human licensing and hosting review. Read the [documented workshop comparison](docs/workshop-reference-case-study.md) for a pinned Indico/pretix example. The research CLI successfully returned two GitHub candidates in [PR CI](https://github.com/ahpa5246-lgtm/Senior-level-website-development-skills/actions/runs/39031574932); this is *retrieval evidence*, not working-application proof. A private project brief must never be sent to a public GitHub search or saved in a public CI log.

**Current packet CLI requirement:** Pass `--evidence-dir /path/to/private-review-files` when running `python3 scripts/portfolio_intake.py packet --input PRIVATE-plan.json --output PRIVATE-manager-handoff.json --evidence-dir /path/to/private-review-files`. Every reviewer must provide an existing relative `artifact_path` and a correct SHA-256 of that exact file. The validator checks file bytes but cannot establish that an independent specialist conducted the review. Keep reviewer files outside the public repository.
