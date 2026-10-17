# Migration and confidentiality ledger

The canonical **code and instructions repository** is now `Senior-level-website-development-skills`. The former `autonomous-project-manager` was **private** while this destination is **public**. This migration preserved reusable functionality and intentionally did NOT export live confidential history.

## Copied from the private manager main branch

- Policies: `AGENTS.md`, `FACTORY_POLICY.md`, `QUALITY_POLICY.md`, `NEW_PROJECT_INTAKE.md`, `ENGINEERING_INTAKE_CONTRACT.md`, all under `manager/`.
- Scripts: `manager/scripts/reconcile_intake_packet.py` and `manager/scripts/plan_reviewed_day.py`.
- Tests: `manager/tests/test_reconcile_intake_packet.py` and `manager/tests/test_plan_reviewed_day.py`.
- Documentation: `manager/docs/SENIOR_CONDUCTOR_DAY_PLAN.md`.

## Copied from the private manager Supervisor V2 development branch

- `manager/SUPERVISOR_V2.md`, `manager/SCHEDULED_MANAGER_PROMPT.md`, `manager/docs/AUTOMATION_MATURITY.md`.
- `manager/prompts/LONG_GOAL_RUNNER.md`, `manager/prompts/SUPERVISOR_V2_RUN.md`.
- `manager/templates/PROJECT_MEMORY_TEMPLATE.md` and `manager/templates/TASK_PACKET_TEMPLATE.md`.

These reusable instructions were modified where necessary to point into the **same repository**. The original private source repository has not been deleted or made public.

## New unified-repository features

- `manager/scripts/bootstrap_private_state.py` initializes empty locally protected state.
- `manager/state-templates/` contains generic, fictional/empty queues, current task, blockers, work logs and improvement backlog.
- `manager/tests/test_bootstrap_private_state.py`, `.github/workflows/manager-tests.yml`, root `.gitignore`, and the unified `manager/README.md` provide regression tests and an owner-facing entry point.
- Root `AGENTS.md`, `README.md`, the Arabic getting-started guide, project operating model and skeptical conductor instructions now point to `manager/` **instead of a second running code repository**.

## Deliberately NOT published to public Git

The old private main branch's actual `PROJECT_QUEUE.md`, `CURRENT_TASK.md`, `AUTONOMOUS_TASK_QUEUES.md`, `BLOCKERS.md`, `WORK_LOG.md`, `CONTINUOUS_IMPROVEMENT_BACKLOG.md`, and project-specific plans, audits and handoffs from `HANDOFFS/` and `AUDITS/`. Other historical experimental branches containing ongoing project-specific state were not automatically republished either. Publishing these verbatim could reveal private repository links, operational history, internal issues, unpublished designs or personal/business information.

This means **the codebase is unified, not the private historical runtime data**. No runtime module fetches or depends on the old manager GitHub repository. Current state must be kept in `manager/.state/` (locally gitignored) or an explicitly authorized private store, with the implications of private-state backup/resumption documented in `manager/README.md`.

## Security and verification limits

No secrets, raw book PDFs, medical customer data or payment credentials were migrated. Reusable scripts are dependency-free Python and have CI unit tests. The Python planner creates a **proposal**, not actual clock scheduling or a supported Codex Cloud worker. Never claim automatic wake-ups, quota bypass, merged deployments or completed user projects without real platform evidence.
