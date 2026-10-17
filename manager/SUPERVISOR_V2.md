# Supervisor V2 — Near-Zero-Touch Project Orchestration

## Purpose
Supervisor V2 converts a durable project roadmap into long, bounded Codex work packets. The owner supplies intent once; the supervisor plans, monitors, validates, records, and prepares the next packet without repeatedly asking what to do.

## Control loop
1. Read manager policy and the target repository's `.project-manager/` memory.
2. Reconcile the roadmap with Git history, open issues/PRs, CI, and completed acceptance gates.
3. Select only READY work whose dependencies are satisfied.
4. Build one long task packet containing several coherent milestones, explicit tests, stop conditions, and prohibited actions.
5. Start through a supported Codex Cloud integration when verified; otherwise mark the packet `MANUAL_START_REQUIRED` and notify the owner once.
6. Monitor acknowledgement, commits, PR, reviews, and CI without duplicating work.
7. Request at most one focused repair for a concrete failed gate.
8. When gates pass, preserve the draft PR as `AWAITING_HUMAN_REVIEW` and prepare the next repository packet.
9. Never merge, deploy, spend, expose secrets, change visibility, or bypass usage limits.

## Autonomy target
- Routine engineering choices: autonomous.
- Ambiguous but reversible choices: choose the conservative option and record it.
- Secrets, payments, login, production, medical/legal/privacy, destructive changes, or product-scope decisions: stop and notify.
- Aim for one or two owner interventions per day, not zero safety oversight.

## Platform boundary
The supervisor must not claim it can click Codex Cloud controls unless a supported integration actually completed the action. GitHub `@codex` delegation may be used only after a delivery probe succeeds for that repository. Otherwise it prepares an exact long-running Cloud prompt and preserves resumable state.

## Long-packet rules
A packet should normally contain 3–10 coherent milestones, be independently testable, and be large enough for an extended session. It must not combine unrelated repositories or hide human-only work. Every packet includes:
- repository and base branch;
- objective and non-goals;
- ordered milestones and dependencies;
- acceptance gates;
- commit strategy;
- retry and resume instructions;
- stop/escalation conditions;
- final draft-PR requirements.

## Resumability
Codex must commit after each validated milestone and update durable state. A resumed run reads Git history and the work log before acting, skips completed work, repairs dirty/incomplete work, and continues at the first unmet gate.

## Unified repository usage
Read root `AGENTS.md`, then `manager/AGENTS.md`, `manager/FACTORY_POLICY.md`, `manager/QUALITY_POLICY.md`, and locally protected `manager/.state/`. Do not use the old project-manager repository as a runtime dependency. This policy alone does not activate a scheduled Codex integration.
