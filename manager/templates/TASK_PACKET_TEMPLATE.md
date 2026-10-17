# Long Codex Task Packet

Packet ID: `<repo>-<sequence>-<slug>`
Repository:
Base branch: `main`
State: `READY`
Estimated scope: extended session

## Objective
A measurable outcome, not “improve everything.”

## Context to read
- Repository instructions and `AGENTS.md`
- `.project-manager/PROJECT_BRIEF.md`
- `.project-manager/ROADMAP.md`
- `.project-manager/AUTONOMY_POLICY.md`
- `.project-manager/ACCEPTANCE_GATES.md`
- Git history, active branches, issues, PRs, CI

## Ordered milestones
For each milestone specify dependencies, files/surfaces, behaviour, tests, documentation, and completion evidence.

## Operating loop
1. Reconcile the packet with current Git state.
2. Skip work already proven complete.
3. Implement the first unmet milestone.
4. Run focused gates, repair attributable failures, and self-review.
5. Commit with a descriptive message.
6. Update durable project memory.
7. Continue to the next milestone without routine confirmation.
8. Stop only at packet completion, usage/platform limit, or a red-category blocker.

## Universal gates
- Reproducible lockfile installation.
- Applicable tests, typecheck, lint, format, and build pass.
- No secret, personal data, generated dependencies, accidental artifacts, paid service, or unrelated scope.
- Error paths, resource bounds, accessibility/security, documentation, and rollback are reviewed.
- Exact evidence is recorded; unavailable checks remain unresolved.

## Prohibited
No merge, deployment, payment, account creation, visibility change, secret handling, history rewrite, destructive change, or unsupported legal/medical/privacy/production claim.

## Final delivery
Create one feature branch and one draft PR to `main` with summary, commits, exact commands/results, risks, limitations, manual actions, and rollback. If PR creation is unavailable, preserve clean commits and expose the manual Create draft PR action.
