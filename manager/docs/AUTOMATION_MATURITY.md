# Automation Maturity Model

## Level 0 — Manual
Owner writes and sends every prompt.

## Level 1 — Durable memory
Project intent, roadmap, gates, decisions, blockers, and logs live in Git.

## Level 2 — Automatic planning
Supervisor reconciles Git evidence and turns READY roadmap items into long packets.

## Level 3 — Monitored Cloud execution
Owner starts a prepared long goal; supervisor monitors PR/CI and prepares follow-ups.

## Level 4 — Verified delegated start
A repository-specific GitHub-to-Codex delivery probe has successfully produced a writable branch and draft PR. Supervisor may start later bounded packets through that verified path.

## Level 5 — Near-zero-touch portfolio
Supervisor plans, delegates, validates, pauses blocked work, advances the queue, and sends one digest. Human intervention remains mandatory for merge, deployment, secrets, payment, destructive actions, and sensitive product decisions.

## Promotion gates
Never promote a repository based on an acknowledgement alone. Require:
- Cloud task linked to the intended repository;
- commits delivered to GitHub;
- draft PR created or updated;
- CI/test evidence visible;
- resume behaviour tested;
- no duplicate task on retry.

A failed delivery demotes the repository to Level 3 until a new mechanism is explicitly re-proven.
