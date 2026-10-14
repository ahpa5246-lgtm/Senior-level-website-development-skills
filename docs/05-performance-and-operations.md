# Low-end device budgets and recoverable operations

Basis: web.dev Web Vitals; DDIA workload/scaling discussions; Google resilience/recovery/testing chapters. Byte and lab-profile proposals below are local starting budgets, not standards.

## Measure user outcomes

Current good Core Web Vitals thresholds: LCP <=2.5s, INP <=200ms, CLS <=0.1, evaluated at the 75th percentile with mobile/desktop segmentation. Lab tests diagnose controlled conditions; field measurements reflect actual users. A Lighthouse score does not prove field INP or universal device quality.

Before coding, record representative routes, initial and repeat visits, dataset size, authentication state, geography, browser, CPU/network profile and measurement method. Include a real low-end device when available. If unavailable, report that limitation and use recorded throttling, not a vague “tested on mobile.”

## Proposed constrained profile and budgets

A starting laboratory profile: 360px viewport, 4x CPU slowdown, 1.6Mbps downstream, 750Kbps upstream, 150ms latency; document the tool's units and throttle mechanism. This is an approximation, not a hardware equivalence.

| Budget | Initial proposal | How to inspect |
| --- | --- | --- |
| Route initial JS transfer | <=150KB compressed for ordinary content/task pages | Production network capture and bundle report |
| Initial total transfer | <=1MB on the critical route | Cold-cache network trace |
| Fonts | One family where practical, only used weights/scripts, <=100KB initial transfer | Font requests and fallback inspection |
| Main-thread work | Investigate tasks >50ms; bound long list/filter work | Interaction trace on constrained CPU |
| Backend latency | Establish route-specific p95/p99 at stated load | Load test plus query/dependency breakdown |

These proposals must be adapted before release: an image-heavy portfolio and a field form differ. Do not silently loosen a budget after failure; document the user benefit, measured cost and alternative. Thresholds for API latency, memory and availability must come from the workload and budget, not invented universal numbers.

## Spend resources deliberately

Use responsive image variants, modern supported formats and explicit dimensions. Prioritize the LCP image; do not lazy-load it by habit. Defer below-fold media and optional widgets. Prefer native browser capabilities and server rendering when they reduce client work. Split expensive route-specific code; check actual chunks because excessive splitting can create waterfalls.

Do independent reads in parallel only where dependencies, quotas and resource ceilings allow. Cap concurrency. Add caching with key scope, freshness, invalidation and privacy rules. Never share a personalized response across users. Consider request deduplication; cache correctness takes priority over a benchmark.

Animate cheap properties where appropriate, measure rendering/compositing, and provide reduced-motion/static alternatives. Avoid autoplay media, full-screen shaders and large blur surfaces unless they provide a demonstrable benefit within the budget. Virtualization can help long lists but introduces focus/accessibility complexity; pagination may be better.

## Operate the real service

Validate required configuration on startup without printing secrets. Expose meaningful health/readiness signals without leaking internal details. Track request rate, errors, tail latency, saturation and core business success; measure queue age where relevant. Alert on actionable user impact with an owner and runbook, not every noisy metric.

Use structured redacted logs and correlation IDs. Define retention and access. Make deployments reproducible; run production-mode smoke tests after deployment. Roll back compatible application changes to a known safe version; do not reintroduce a known vulnerability just to regain availability. Database recovery is a distinct procedure from app rollback.

Rehearse restore into an isolated environment, verify data integrity, record actual RPO/RTO and protect backup credentials. Test failure and load safely in authorized nonproduction environments first. Graceful degradation must preserve truth: “saved locally, pending sync” is different from “saved to server.”
