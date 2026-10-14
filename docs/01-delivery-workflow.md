# Delivery workflow: decisions followed by evidence

## 1. Discover the outcome

Describe the users, their tasks, success conditions, sensitive data, operating context, maintainers and budget. Separate launch requirements from future possibilities. Inventory existing functionality before changing it. Define whether the deliverable is a prototype, static publication, internal tool or production service.

Gate: each core journey has an observable result and an owner; assumptions are recorded. “Build a modern website” is insufficient.

## 2. Model behavior before screens

For each feature write the actor, preconditions, inputs, authorization rule, state transition, persistence, side effects and recovery path. Specify loading, empty, validation error, permission denied, timeout, success and conflict states. Inventory all navigation destinations and controls, including tabs, pagination, filters, downloads and account actions.

Gate: no control promises an undefined outcome. See templates/feature-contract.md.

## 3. Choose architecture and design together

Rank the few quality attributes that drive structure: data integrity, accessibility, latency, availability, cost, maintainability. Security obligations remain baseline requirements, even when absent from the top three business priorities. Record expected load rather than assuming millions of users. Choose a rendering approach by content, search needs and interactivity. Review content hierarchy before styling.

Gate: architecture decision and design brief explain alternatives, costs and revisit triggers. A modular monolith is a useful starting hypothesis, not a universal command.

## 4. Build a complete vertical slice

Implement one core journey through UI, boundary validation, authorization, domain rules, persistence and external integration. Exercise a valid request, invalid input, another user's object, duplicate submission and dependency failure. A test double is useful for development but cannot prove the provider works.

Gate: a user can complete the journey, refresh and observe durable state where required; unauthorized users cannot perform it through direct API calls.

## 5. Expand and verify by risk

Add remaining contracted features using established boundaries. Use focused unit tests for business invariants, integration tests against real persistence, and a small reliable E2E suite for critical outcomes. Add accessibility, resource-budget and permission checks. Inspect browser console/network and server errors. Manual reviews complement automation.

Gate: every launch requirement maps to evidence. Unrelated speculative refactoring is excluded.

## 6. Release and operate

Build in production mode; validate configuration without exposing secrets. Apply compatible migrations, deploy, smoke-test, monitor user outcomes, and retain a safe rollback target. Rehearse restoration where data loss matters. Include runbooks and ownership.

Gate: release evidence lists commit, environment, commands, measured outcomes, unresolved risks and rollback/restore steps.

## Applying this outside websites

Replace routes and controls with CLI commands, robot actions, jobs or service operations. Keep the same chain: requirements -> explicit state transitions -> trust boundaries -> resource budgets -> observable acceptance -> recovery. UI/SEO checks may be N/A; integrity and honest evidence remain relevant.
