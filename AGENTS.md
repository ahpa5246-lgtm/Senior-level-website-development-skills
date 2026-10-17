# Engineering instructions for agents using this framework

Read README.md, docs/01-delivery-workflow.md and the relevant domain guides before work. Read the target project's own instructions and existing code before proposing changes. This repository supplies guidance; it does not authorize external actions.

## Required behavior

1. Identify audience, core journeys, data ownership, real persistence requirements, device/network constraints, scope and non-goals. Ask only questions whose answers materially change implementation; record reversible assumptions.
2. Build a feature inventory: route/control -> user outcome -> trusted operation -> stored data -> permission -> all UI states -> acceptance evidence.
3. Document the smallest viable architecture and at least one credible alternative. Do not create microservices, queues, caches or state libraries without a concrete trigger.
4. Before implementation, define security boundaries and negative tests for identity, object access, tenant isolation and business invariants. Secrets stay outside public bundles and logs.
5. Establish a design direction from content and tasks. Describe what to build, why it fits, and what it costs to render. A color substitution is not a design strategy.
6. Implement vertical slices from interaction to trusted behavior and persistence. Do not mark a feature complete because a modal opens or a success toast appears.
7. Check applicable matrix items. Record pass/fail/N/A with evidence; N/A needs justification. No fabricated commands, metrics, citations or screenshots.
8. Validate the production build and critical journeys. Report commands, environment, commit, actual outcomes and remaining risks. Distinguish mocks, sandbox integrations and live production behavior.
9. Protect low-end devices: budget JavaScript, images, fonts, CPU work and request volume; measure representative routes and interactions under a recorded constrained profile.
10. End with a truthful delivery report. A blocker means partial delivery, with a concrete next action. Never conceal an unimplemented tab, mocked endpoint, unavailable credential or failed check.

## Release blockers

Unapproved scope gaps in a core journey; fake success; broken object/tenant authorization; leaked credentials; unsafe money/inventory transitions; destructive untested migration; failed production build; inaccessible core interaction; unknown restore procedure where persistent data matters.

Do not convert advisory heuristics into universal laws. Static sites need no invented API; internal tools need no public SEO; every helper does not need its own class or test. Prefer outcome and invariant tests over implementation mirrors.

## Owner-guided discovery and portfolio routing

For new projects or major architecture/hosting changes requested by non-programmers, read [the skeptical conductor](prompts/skeptical-conductor.md), [portfolio operating model](docs/portfolio-operating-model.md), and [20-question contract](config/20-questions-ar.json) before generating target code. Get user constraints and independent evidence; run the actual intake validator. Treat its READY_FOR_PLANNING state only as permission to plan, not to deploy or spend. Reuse working components; check external licenses and operating economics. Existing bounded bug fixes can proceed under existing project policy without repeating the entire questionnaire.


## Noncoder conductor V2: required default entrypoint for substantial work

Use docs/START_HERE_NONCODER_AR.md and scripts/project_conductor.py before proposing a new application or significant new hosting/back-end architecture. Source-specific, conditional verification checks live in config/senior-gates.json. Run the actual tests; do not claim a check succeeded based on a written description alone.

When the user provides actual GitHub repository research JSON or a hosting cost scenario report, use blueprint --references-file / --cost-file to join evidence into the owner report, and show which claims remain unverified. A GitHub license string is not permission to reuse all code/assets. A cost subtotal is not verification of provider rates. Always preserve open unknowns and owner limits.

Never place owner-specific 20-question answers, account tokens, live customer records, reviewed handoff packets or provider quotes in this PUBLIC repository. Keep read-only analysis separate from autonomous implementation. The private manager's day-plan CLI creates illustrative slots, not an actual Cloud scheduler; only a verified runtime can start Codex after live reconciliation and the existing no-spend/no-merge rules.


## Mandatory unified supervisor entrypoint (one repo only)
All reusable supervisor policies, Codex long-session prompts, packet validation, private-state bootstrapping, day planning and tests now live under [manager/](manager/README.md) **in this same repository**. Never require or instruct the user to visit the former `autonomous-project-manager` repository for new work. For meaningful engineering work, read `manager/AGENTS.md`, `manager/FACTORY_POLICY.md`, `manager/QUALITY_POLICY.md`, `manager/ENGINEERING_INTAKE_CONTRACT.md`, and `manager/SUPERVISOR_V2.md`. Initialize local state with `python3 manager/scripts/bootstrap_private_state.py --destination manager/.state` if absent; do not fabricate or auto-populate authorized projects. Current owner-specific queue, logs, tokens, private interviews, handoffs and customer records MUST NOT enter this public Git history. One active Codex implementation globally. Human approval still required before merges, deployments, costs, secret handling or sensitive decisions; a drafted daily plan is NOT an actual worker or scheduled automation.


## Mandatory real-product UX/visual comparison at each UI milestone
For any significant website or desktop/mobile UI, follow [competitive visual QA](docs/competitive-visual-qa-ar.md) before planning, and re-check after each major UI change and before claiming release readiness. Review **released, reputable, directly comparable real products** (at least two direct + an aspirational reference for multi-workflow apps), not only GitHub demos or synthetic AI designs. Use official feature/visual sources, record dated evidence and a competitor-by-journey gap/decision. Compare whole information architecture: named destinations for distinct workflows, progressive disclosure, whitespace/reading comfort, type hierarchy including Arabic font, semantic colors, purposeful original 2D illustration vs clutter, loading/empty/error states, accessibility and low-end asset cost. A complex five-flow product should not be one giant cramped form; however do not force multiple pages on genuinely simple applications. Run `python3 scripts/visual_quality_gate.py --input ... --evidence-root ...` at planning AND implementation; the implementation audit must reference the actual app commit, screenshots and observed tasks. `PASS_EVIDENCE_STRUCTURE` is evidence-structure validation, not proof of superior aesthetics. Block UI review when critical evidence is absent; never forge benchmarks or claim it passed without seeing the screenshots.
