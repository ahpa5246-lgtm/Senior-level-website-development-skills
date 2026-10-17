# Adding a New Project

The easiest way for the owner to add a project is to send the supervisor:

1. The GitHub repository link.
2. One sentence describing the goal.
3. The first feature or problem to prioritize.
4. Any deadline.
5. Anything forbidden, paid, private, or requiring approval.

Everything else may be inferred conservatively from the repository.

## Minimal copyable intake

```text
Repository: https://github.com/OWNER/REPO
Goal:
First priority:
Deadline: none
Important constraints:
```

## Supervisor intake procedure

Before editing a newly supplied repository, the supervisor must:

1. Verify repository ownership/access, visibility, default branch, license, active issues/PRs, workflows, and latest commits.
2. Check for `AGENTS.md` and repository-specific instructions.
3. Run a read-only baseline audit covering build, tests, security, accessibility, documentation, and release state.
4. Add one row to `PROJECT_QUEUE.md`.
5. Create one persistent “Autonomous execution queue” issue in the target repository; never create duplicates.
6. Add the issue and ordered milestones to `AUTONOMOUS_TASK_QUEUES.md` and this backlog.
7. Define one small first milestone with acceptance tests in `CURRENT_TASK.md`.
8. Implement only on a feature branch and one draft PR; never write target implementation directly to `main`.
9. Record exact commits, CI runs, artifacts, blockers, and required human actions in `WORK_LOG.md`.

## Automatic safety defaults

Unless the owner explicitly says otherwise, the supervisor assumes:

- free tooling/runners only;
- no merge or public deployment;
- no secrets pasted into chat or GitHub;
- no billing, purchases, account enrollment, destructive migration, visibility change, or history rewrite;
- no real medical/personal data or unsupported legal/clinical claims;
- no model promotion based on one run.

## Senior-skills intake gate for substantial new products

The minimal form above is sufficient to **register an idea and perform read-only audit**. It is not sufficient to authorize developing a new publicly used app or major hosting architecture. For new product work, follow [ENGINEERING_INTAKE_CONTRACT.md](ENGINEERING_INTAKE_CONTRACT.md): ask 20 nontechnical questions, assess known/unknown user and budget constraints, compare documented open-source references, and obtain independent feasibility/security/architecture/design reviews. A validated private task packet may then seed the project queue; it may not override current task/PR state or existing approval boundaries. Keep existing safe maintenance work available without retrospective questionnaire requirements.
