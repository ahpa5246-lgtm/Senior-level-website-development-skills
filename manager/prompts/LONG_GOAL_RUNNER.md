# Long Goal Runner Prompt

Use this as the stable Codex Cloud entry prompt after replacing placeholders.

```text
/goal

Work autonomously for an extended session on <REPOSITORY>.

Read repository instructions, Git history, open work, and every file under .project-manager/ before editing. Reconcile CURRENT_MILESTONE and TASK_QUEUE with actual evidence. Never repeat completed or active work.

Execute the current long task packet in dependency order. After each coherent milestone:
1. run focused validation;
2. repair failures attributable to the change;
3. self-review scope, correctness, security, accessibility, error handling, resource bounds, and regressions;
4. create a descriptive commit;
5. update .project-manager/CURRENT_MILESTONE.md and WORK_LOG.md;
6. continue automatically to the next unmet milestone.

Do not ask for routine confirmation. For reversible ambiguity, choose the most conservative option and record the decision. Stop for login, secrets, payment, deployment, merge, visibility, destructive migration, unclear ownership, unsupported medical/legal/privacy/production decisions, usage limit, or unavailable required source.

Never merge or deploy. At completion, run every applicable acceptance gate from a clean state and create one draft PR to main with exact evidence, risks, limitations, manual actions, and rollback. If PR creation is unavailable, leave clean commits and expose Create draft PR.

Continue until the packet passes, a genuine red-category blocker is reached, or the platform stops the run.
```
