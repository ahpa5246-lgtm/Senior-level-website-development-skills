# Quality Policy

## Universal gates
A milestone is not ready for human review unless all applicable gates pass:

1. The scope matches `CURRENT_TASK.md`; unrelated refactors are excluded.
2. Dependency installation is reproducible and uses the committed lockfile.
3. Type-check succeeds.
4. Formatter check succeeds.
5. Linter succeeds when configured.
6. Unit/integration/end-to-end tests relevant to the change succeed.
7. Production build succeeds.
8. No credentials, private data, generated dependency directories, or large accidental artifacts are committed.
9. Accessibility and security checks appropriate to the feature are executed.
10. Documentation states setup, test commands, limitations, and remaining risks.
11. CI evidence or exact local/cloud command output is recorded.
12. A pull request contains summary, risk assessment, validation evidence, and rollback notes.

## Review policy
- Codex that implemented a change must perform a self-review.
- A separate review pass must inspect correctness, security, regressions, accessibility, tests, and scope.
- P0/P1 findings block progress.
- Failed or unavailable checks must be reported as unresolved, never silently treated as passed.
- The manager never merges automatically.

## Medical project gates
- No real medical or personal data in fixtures, tests, logs, screenshots, URLs, or analytics.
- No operational claims about encryption, anonymity, clinician verification, emergency response, privacy rights, or message delivery without implemented evidence and human approval.
- Mock content is visibly marked fictional.
- Emergency and clinical wording requires qualified local human approval.
- Keep preview indexing disabled until production authorization.

## Machine-learning/training gates
- Fix random seeds where practical.
- Record environment, dependencies, configuration, evaluation protocol, and checkpoint origin.
- Separate training and evaluation data/opponents.
- Preserve checkpoints and metrics so interrupted jobs resume.
- Compare against a baseline with repeated evaluations.
- Never claim improvement from a single noisy run.


## Mandatory published-product comparison for substantial UI work
A UI milestone cannot be marked `AWAITING_HUMAN_REVIEW` on the strength of unit tests and a pretty mockup alone. Inspect at least two **released direct competitors** plus a suitable high-quality visual reference for multi-flow products. Compare user tasks, navigation hierarchy, page grouping, information density, whitespace, Arabic typography, semantic colors, meaningful 2D illustration, responsive window states, empty/loading/error states and accessibility; provide dated official source links and actual app screenshots at the implemented commit. Use `scripts/visual_quality_gate.py` and `docs/competitive-visual-qa-ar.md` in the one Senior Skills repository. Stage `implementation` or `release_review` cannot pass with missing actual evidence. Enforce a newly reviewed comparison after major UI milestones; this is NOT a running external benchmarking crawler. A `PASS_EVIDENCE_STRUCTURE` output only proves the required record shape, not that human visual examination or task testing was actually performed. Serious UX gaps remain human-review blockers.
