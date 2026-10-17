# Built-in Autonomous Project Manager — one repository

This folder contains the engineering supervisor previously kept in a **separate private GitHub repository**. **The only code repository you need to provide to ChatGPT/Codex now is [Senior-level-website-development-skills](../README.md).** The previous private repository is archival and is NOT required to run these tools.

## What it does today

- Reads the senior engineering intake from root `scripts/project_conductor.py`, including 20 Arabic noncoder questions, architectural choices, cost scenarios, repository research, licensing and conditional verification gates.
- Uses `scripts/portfolio_intake.py packet` to create evidence-backed, independently reviewed task packets.
- Uses `manager/scripts/reconcile_intake_packet.py` to check ownership, task IDs, queue state and SHA-256 review evidence **without changing a target repository**.
- Uses `manager/scripts/plan_reviewed_day.py` to propose bounded UTC implementation/review slots and read-only fallback options when another project is blocked.
- Contains Supervisor V2 instructions for long bounded Codex sessions, project memory, safe resumption and draft PRs.

**Not installed:** an always-on scheduler, a direct Codex Cloud execution integration, independent human reviewer approval, provider-pricing verification, actual code builds for other target projects, or automatic deployment. A proposed day plan never executes itself. Do not claim otherwise.

## One-step first use

From the root of your local checkout:

```bash
python3 manager/scripts/bootstrap_private_state.py --destination manager/.state
python3 -m unittest discover -s manager/tests -v
```

The first command creates EMPTY owner-private queue/state templates in `manager/.state/`, plus a copy of factory policy. The folder is ignored by Git. On a **new computer or fresh cloud checkout**, it must be re-created or recovered from an owner-controlled private backup. This repository is public and must never be used as an unencrypted history of real customer data, private project discussions or tokens.

To add a project, ask your assistant to inspect the actual GitHub repo, confirm your ownership/permissions, then add a row to the private `manager/.state/PROJECT_QUEUE.md`. **An empty or illustrative queue grants no authorization.** For large new applications, complete the root project's 20-question interview and four real reviews first. For a small bug fix in an existing project, follow `NEW_PROJECT_INTAKE.md` and do not force a redundant interview.

## Full workflow with the assistant

1. Tell the assistant: “Use this repository only. Read the root AGENTS.md and manager/AGENTS.md. Interview me in simple Arabic about my project and budget.”
2. Run the root intake and cost/repository research tools; save outputs outside public Git.
3. The assistant drafts architecture options, a concept brief (a generated image is **separate**, not proof of working code), executable milestones with acceptance criteria and an owner-readable risk report.
4. After reviewing real evidence, the root packet generator prepares the handoff. Four independent evidence files must be available and have matching hashes.
5. The built-in manager validator reads `manager/.state/PROJECT_QUEUE.md`. Example (paths are private placeholders):

```bash
python3 manager/scripts/reconcile_intake_packet.py \
  --packet /PRIVATE/reviewed-handoff.json \
  --evidence-dir /PRIVATE/review-files \
  --manager-root manager/.state \
  --out /PRIVATE/reconciled.json
```

6. After validation, generate an illustrative daily plan (it **does not** start Codex):

```bash
python3 manager/scripts/plan_reviewed_day.py \
  --packet /PRIVATE/reviewed-handoff.json \
  --evidence-dir /PRIVATE/review-files \
  --manager-root manager/.state \
  --start 2026-10-18T09:00:00+03:00 \
  --minutes 240 \
  --milestone-minutes 60 \
  --review-minutes 15 \
  --out /PRIVATE/day-plan.json
```

7. The assistant uses `manager/prompts/LONG_GOAL_RUNNER.md` and `manager/templates/TASK_PACKET_TEMPLATE.md` to prepare ONE bounded task for a verified supported Codex runtime, after checking the latest GitHub task/branch/PR/CI state and the user's authority. No duplicate jobs, no paid service, no deployment, no release or merger without explicit user approval. GitHub comments alone are not proof that Codex started.

## Where everything now lives

| Need | Single-repository location |
|---|---|
| Noncoder interview, architecture, errors and costs | `scripts/`, `config/`, `docs/` |
| Supervisor instructions and safety | `manager/AGENTS.md`, `manager/FACTORY_POLICY.md`, `manager/QUALITY_POLICY.md` |
| Full Supervisor V2 loop | `manager/SUPERVISOR_V2.md` |
| Task packet reconciliation | `manager/scripts/reconcile_intake_packet.py` |
| Safe proposed day schedule | `manager/scripts/plan_reviewed_day.py` |
| Long-session Codex prompts | `manager/prompts/` |
| Project memory and task templates | `manager/templates/` |
| Private project queue / state / blockers | Local **gitignored** `manager/.state/` |
| Tests for all copied supervisor scripts | `manager/tests/` |
| CI | `.github/workflows/manager-tests.yml` |

## What was NOT copied out of the old private GitHub repository

The private source contains active `WORK_LOG.md`, `PROJECT_QUEUE.md`, `CURRENT_TASK.md`, `BLOCKERS.md`, `AUTONOMOUS_TASK_QUEUES.md`, project audits, per-project handoffs, and project-specific experimental roadmaps. These files were **deliberately not published** because the destination is public, and they may disclose private project information. The original private repository remains unchanged as a private archive. The workflow code no longer requires that repository.

If you want all actual historical state inside ONE GitHub repository too, its visibility must first be changed to **private** with separate explicit approval and a confidential-data audit; until then a public repo cannot safely provide private cross-device state storage.

## Before claiming autonomous Codex operation

Do an actual supported service integration end-to-end: prove delegated start, task acknowledgement, commit, PR, CI result, stoppage handling, safe retry, no duplicated billing/jobs, and human-gated merge. `manager/docs/AUTOMATION_MATURITY.md` documents maturity levels. A command or recurring prompt alone is not proof of running Codex.
