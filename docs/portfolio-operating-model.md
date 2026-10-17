# Non-coder project intake and portfolio handoff

This framework is an engineering control system, not a model fine-tune, a 24-hour-running agent, a substitute for human judgment or an authorization to deploy. Never put owner answers, book contents, credentials or sensitive project details in this public repository.

## Five roles and their concrete outputs

1. **Adaptive interviewer:** Ask the 20 plain Arabic questions in [config](../config/20-questions-ar.json), with only relevant domain follow-ups. Accept "I don't know"; document the effect. Do not assume the budget, concurrency, storage, data sensitivity or intended release mode.
2. **Independent skeptic and feasibility analyst:** Disprove the preferred approach if possible. Compare at least two technically plausible designs and a simpler non-custom solution. Identify fatal limits, missing data and likely operational costs. For workshop video, compare embedding/using an external meeting service against self-hosting SFU/TURN, including attendance, minutes, recordings and bandwidth.
3. **Solution analyst / design director:** Explain the future site in simple Arabic: visitor and admin journeys, scope, differences from actually inspected reference products, slow-network behavior, identity, privacy, mobile layout, essential features, postponed features and failure states. Produce a sitemap, wireframes and, **only if image-generation is available**, clearly labeled concept images. A concept image is not a working screenshot.
4. **Senior architect and task planner:** Choose the smallest warranted architecture and explain alternatives and trade-offs. Define modules by coherent business capability, not by database entity. Specify exact files/paths where the target codebase is known, risks, requirements, test IDs, dependencies, clear acceptance criteria, rollback and 5–15 coherent tasks per safe batch. More work is not evidence of more quality.
5. **Independent reviewers + Codex supervisor:** Recheck finance, licensing, security, architecture, design and exact test evidence. Only validated task packets move to the **private** portfolio manager. Codex executes authorized work in a branch, verifies each vertical slice, retains checkpoints and visits another eligible project when blocked. It must not merge, deploy, purchase, reveal secrets or evade limits autonomously.

## Architecture and hosting as a user requirement

A declared zero monthly budget is a hard constraint, not a preference. Differentiate a disposable private demo from a public persistent service. A pricing estimate requires sourced, dated quotes and real usage assumptions; no quoted component means **unpriced**, never zero. Review hosting, backend, DB read/write/storage, network egress, emails, domain and renewal, backups, monitoring, video streaming, TURN, uploads, paid AI calls and support. Compare **normal, launch-day peak and failure/recovery** cases. Show monthly plus annualized setup/domain costs and possible overages with uncertainty.

The conversation's $50/month hosting quote is one person's estimate, not a universal minimum. An event-registration site plus an externally hosted workshop can cost much less than implementing group video conferencing; actual feasibility and price depend on current provider terms. A free plan may sleep, enforce resource ceilings or restrict commercial production.

Architecture choices: static pages for public content without trusted writes; modular monolith for small authenticated transactional products; asynchronous jobs only when workload requires; independently deployed services only when proven independence/scale/deployment needs outweigh costs. Distinguish *logical* modules from independently deployable components. Shared schemas or synchronous calls create coupling. Protect identity, object/action authorization, integrity under concurrency, recovery/retention, keyboard/RTL access and p95/p99 latency.

## Open-source reference discovery (not blind cloning)

For each candidate found on GitHub record URL and immutable commit, license plus asset attribution, security advisories, ongoing maintenance, backend dependencies, container/runtime requirements, matching workflow, realistic costs, responsiveness and evidence that important buttons persist data. Compare: study design only, integrate bounded library, adapt correctly licensed project, or build independently. A project lacking an explicit license is **not automatically reusable**. Never expose the private medical site's requirements inside a public issue.

Use [500 pitfalls](500-senior-pairs-ar.md) as a *conditional* risk catalogue, not a requirement to implement every mitigation. Pair them with the existing [100-item evidence-oriented matrix](100-error-matrix.md) and the [book-derived architecture, data and security notes](book-insights.md). The books and the eight chapter summary images are evidence for questions and trade-offs, not permission to republish their text, pages or images.

## Machine gate (working now)

- Get the 20 questions: python3 scripts/portfolio_intake.py questions
- Create owner-only JSON based on [example](../examples/zero-budget-demo.intake.json); answer keys Q01–Q20, kind, release_mode, monthly_budget, one_time_budget, expected monthly_users/peak_concurrent, cost_components, provider_quotes, reference_repositories.
- Assess: python3 scripts/portfolio_intake.py assess --input PRIVATE-intake.json --output PRIVATE-assessment.json
- Status NEEDS_INPUT or NEEDS_EVIDENCE means **no implementation handoff**. The assessment never asserts that it verified actual provider prices or user experience; it only checks declared assumptions and citations.
- Planner adds execution_tasks with ordered dependencies, objective, measurable acceptance and verification. Reviewers supply feasibility, architecture, security, design signoffs tied to **real inspectable artifacts**.
- Packet: python3 scripts/portfolio_intake.py packet --input PRIVATE-plan.json --output PRIVATE-manager-handoff.json
- The private [manager](https://github.com/ahpa5246-lgtm/autonomous-project-manager) must recheck live repository state, code licenses, approvals and budget. The packet does not dispatch Codex itself and always sets release_authorized=false.

## Skeptical red-team: what this still does NOT guarantee

Twenty short answers can omit rare edge cases; domain-triggered follow-ups remain essential. AI systems may agree on a fabricated price or wrong architectural recommendation; ask for independent falsifying evidence and updated official sources. A great-looking mockup does not validate persistence, APIs or legal content. A passing CI run without browser, authorization and recovery exercises does not establish real-world reliability. A beloved open-source app may be unaffordable to host or illegal to relicense. No agent can guarantee that a site is the work of an experienced engineer; the aim is to make claims testable, trade-offs explicit and hidden failure modes visible.

## Mandatory review and autonomy split

The public skills repository contains **general knowledge and reusable checks**. The private manager contains owner answers, costs, working task queues and artifacts. Target repositories contain code, tests and implementation decisions. Model discussions have no authority to ignore the manager's current FACTORY_POLICY.md. Schedule frequency is a configuration and execution fact, not something a prompt alone can guarantee. Codex quotas and deployment permissions remain enforced.
## Actual repository researcher

Run `python3 scripts/github_reference_research.py --query "event registration management" --limit 3 --out local-research.json --live` after getting permission for public metadata searches. It fetches GitHub repository metadata, a concrete branch SHA, top-level file names and the declared license; it does **not** run or copy GitHub code. A license reported in GitHub metadata still requires manual review of the LICENSE text, additional terms and all external media/fonts/assets. Branch timestamps and search results can change; pin a SHA in accepted architectural decisions. See [the workshop comparison](workshop-reference-case-study.md).

The private manager now has a read-only `scripts/reconcile_intake_packet.py` validator for verified review artifacts and existing queue statuses. The CLI requires `--packet`, `--evidence-dir` and `--out`; it refuses duplicate task IDs, stale SHA-256 evidence and currently paused/reviewing project states. Import to live GitHub task tracking remains an explicit separate authorized step.
