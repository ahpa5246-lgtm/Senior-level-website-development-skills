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
