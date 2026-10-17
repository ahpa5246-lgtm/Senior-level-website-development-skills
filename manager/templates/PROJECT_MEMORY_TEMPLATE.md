# Project Memory Template

Copy this directory structure into each managed repository as `.project-manager/`.

## PROJECT_BRIEF.md
- Product purpose:
- Intended users:
- Definition of done:
- Non-goals:
- Deadline or priority:
- Repositories/services involved:
- Human owners:
- Constraints: free-only, no deployment, privacy, etc.

## ROADMAP.md
Use stable IDs.

| ID | Outcome | Dependencies | Priority | State | Evidence |
|---|---|---|---|---|---|
| M1 | Example bounded outcome | none | high | READY | |

States: `IDEA`, `READY`, `PACKED`, `IN_PROGRESS`, `BLOCKED`, `AWAITING_HUMAN_REVIEW`, `DONE`.

## AUTONOMY_POLICY.md
### Green — act independently
Routine tests, documentation, bounded refactors, validation, timeouts, accessibility, CI repairs.

### Yellow — conservative decision plus log
Reversible dependency choice, internal organization, compatible fallback, removal of proven dead code.

### Red — stop and notify
Login, secret, payment, deployment, visibility, destructive migration, merge, unsupported medical/legal/privacy decision, unclear ownership.

## ACCEPTANCE_GATES.md
List exact install, test, type, lint, format, build, security, accessibility, performance, documentation, and rollback gates.

## TASK_QUEUE.md
Keep ordered READY items only after reconciling the roadmap with current Git evidence.

## CURRENT_MILESTONE.md
- Packet ID:
- State:
- Branch:
- Issue/PR:
- Started UTC:
- Last evidence UTC:
- Completed gates:
- Remaining gates:
- Resume point:
- Blocker:

## DECISIONS.md
Record UTC date, decision, alternatives, evidence, reversibility, and affected files.

## BLOCKERS.md
Record owner action required, exact evidence, safe work that may continue, and whether notification was sent.

## WORK_LOG.md
Newest entry first. Include UTC timestamp, action, evidence, commands/results, commits/PR, outcome, and next safe action.
