# Senior engineering intake contract — additive integration

The Senior Skills repository is the **single unified codebase**: reusable skills in the root and built-in supervisor under `manager/`. Private owner-specific state stays in local gitignored `manager/.state/`, never in public Git history.

## Two intake modes

**Existing work / maintenance:** For an already registered project, inspect live code/PR/CI and current owner priorities; do not block a targeted safe bug fix just because a historical project lacks 20 answered questions. Do not increase spend, collect new sensitive data, or change production architecture without new cost/risk review.

**New product or significant architectural change:** Ask nontechnical Q01–Q20 from the public framework, with relevant domain follow-ups. Preserve answer/constraint files in a **private** issue/artifact store only, not in the public skills repository. Unknown answers are allowed but major unknowns block implementation. Follow the stages:

- owner intake and unknowns;
- independent skeptical review of cost, scope, alternative vs build, expected and peak use, maintainability;
- real GitHub reference shortlist with exact commit, license and operational cost check;
- simple user-facing site/app analysis, sitemap, content/state flow and optional clearly labeled visual concept;
- architecture/acceptance-tested task graph with failure cases and execution budgets;
- four evidence-backed reviewer records;
- verified task packet import into this manager's queue.

## Expected packet from the skills repository

Generate through the public tool:

    python3 scripts/portfolio_intake.py assess --input PRIVATE-intake.json --output PRIVATE-assessment.json
    python3 scripts/portfolio_intake.py packet --input PRIVATE-plan.json --output PRIVATE-manager-handoff.json

The packet schema_version must be 1.0, intake_status READY_FOR_PLANNING, contain nonempty tasks each with ID/objective/acceptance/verification/ordered dependencies, and four reviewer entries (feasibility, architecture, security, design) each carrying passed flag, reviewer identity, real HTTPS artifact URL and SHA-256. Review actual artifact contents and hash; do not treat arbitrary self-declared fields as verified evidence.

Each accepted task must be mapped to exactly one current target repository/branch or an owner-approved newly registered repository. Check real open issues, PRs, sessions, branches, CI results, existing backlog and owner priorities BEFORE creating any corresponding issue. Reuse current work rather than duplicating. An old packet must be revalidated after architecture or pricing changes. Do not store source code or secrets in manager task records.

Copy or adapt third-party code only after actual license and version/asset-provenance review. A license warning in the intake report is not approval to reuse.

## Cost and release gates

Provider prices in a packet are owner-supplied, **not automatically verified** by the Python validator. Reinspect official provider pages and rate limits for the target geography and current date. Distinguish free limited previews from public persistent production. Require estimates for normal, spike and recovery; disclose unpriced hosting/database/egress/AI/media/email/storage/backup/domain/operational costs. When a zero-budget owner has an unpriced public requirement, stop implementation of the paid-dependent production path and offer a simple no-cost or third-party integration alternative.

A readiness packet is **not** authorization to create a live service, deploy, merge, purchase, expose secrets, collect real health data or update production DB. Existing FACTORY_POLICY.md and owner-specific policies remain the decisive authority. No autodispatch from this document alone; only the actual authorized Codex/GitHub runtime can dispatch.

## Existing supervisor and scheduling compatibility

- Keep one implementation milestone active globally, unless owner explicitly changes the reviewed concurrency policy.
- Do not rewrite PROJECT_QUEUE.md from a new agent's proposal; reconcile it with current evidence, human pauses and accepted milestones.
- On BLOCKED, MANUAL_CLOUD_DELIVERY_REQUIRED or AWAITING_HUMAN_REVIEW, checkpoint and inspect other eligible projects in the same run without overriding the pause.
- Do not turn 20 questions into 20 coding tasks. The task graph arises from acceptance criteria and dependencies, with bounded batches and review.
- Scheduling frequency is a verified runtime configuration, not a property of the prompt. Preserve current cadence until a working scheduler is measured. Never claim a 15-minute service or a 24-hour Codex session without actual evidence; do not bypass usage limits.
- After each PR, record commit SHA, diff/CI, integration/e2e and resource evidence, user-visible changes, blockers, operational cost, and the next eligible task. Close tasks only when evidence satisfies acceptance.

## Stop cases

No owner budget; unknown real-data handling; unlicensed code targeted for reuse; unresolved critical security/permission defect; provider-cost or capacity mismatch; no recoverable migration/backup for persistent data; fake success state; unreviewed public deployment; contradictory instructions; unauthorized spending. Explain the precise unknown to the owner in ordinary Arabic and continue any safe independent queue work.

## Adoption boundary

This document plus the public repo's tests create the **handoff contract only**. They do not install a background scheduler, provision a VM, guarantee a live Codex session, deploy new projects or prove a new site is secure. The owner should accept the public-skills and private-manager PRs together; after acceptance, perform a dry-run for one harmless private demo and verify no accidental duplicate issues/branches or paid service use.

## Local read-only importer is now implemented

The reviewed packet consumer lives at `scripts/reconcile_intake_packet.py`; it checks evidence files and review hashes in a private directory, exact target repository membership in PROJECT_QUEUE, existing queue status and duplicate milestone IDs. Its `READY_FOR_MANAGER_REVIEW` output is *not a GitHub write*. An unregistered repository must first receive a read-only audit and owner-authorized queue enrollment. This deliberately does not cause a blocked earlier project to be reopened or change the existing one-active-implementation policy.

Before import, reviewer fields must include `artifact_path` relative to the private evidence directory and `artifact_sha256` for the real bytes, plus the original signoff metadata. The public intake CLI validates declared fields only; this private reader makes an additional actual digest comparison, which still cannot prove the reviewer really performed all stated experiments.

## Scenario report chain

For `public_launch` and `internal_production`, the packet must carry `release_mode` and `cost_scenarios_evidence` with relative artifact path and SHA-256 of a report generated by `scripts/hosting_cost_scenarios.py`. The private `reconcile_intake_packet.py` repeats the digest, owner budget/currency and normal/peak/recovery checks. This guards against accidental stale documentation, **not** forged quotes or undocumented charges. If a provider quote cannot be corroborated, do not treat the code gate as independent financial verification.
