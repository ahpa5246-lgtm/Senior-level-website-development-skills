# Case study: a zero-budget student workshop website

**Research snapshot:** 2026-10-17. This is a public comparative **example**, not a decision for any real person or an owner's actual project. The fictional input is [the demo intake](../examples/zero-budget-demo.intake.json). Provider prices and free-tier capabilities were **not** researched or verified here.

## What the owner actually needs

A simple public calendar of workshops and an administrative way to create events. Visitors should be able to submit a registration that persists, receive truthful confirmation, and later access the workshop through an external platform if its terms and features are suitable. Budget: $0/month and $0 setup. Estimated normal use: 80 visitors/month, 10 simultaneous. Both estimates are unvalidated owner assumptions.

**Critical distinction:** A static UI displaying a registration success toast but persisting nothing is not a functioning registration service. Even a lightweight app needs an actual write boundary and appropriate retention/security rules if names or email addresses are stored.

## Checked open-source references

| Reference and pinned inspected revision | Evidence found | License status | Fit and likely downside |
| --- | --- | --- | --- |
| [Indico](https://github.com/indico/indico/tree/ddcf9153dcf2ffe04916ff8e2006098d32ad606d) | Its [README](https://github.com/indico/indico/blob/ddcf9153dcf2ffe04916ff8e2006098d32ad606d/README.md) documents conference workflows, registration forms, schedules, materials, meeting management, integrations with existing video platforms and self-hosting guidance. Root shows test setup and requirements. | [MIT LICENSE](https://github.com/indico/indico/blob/ddcf9153dcf2ffe04916ff8e2006098d32ad606d/LICENSE) inspected. Other assets/dependencies still require checking. | Useful for learning expected user journeys and possibly adopting when an institution can maintain its substantial feature set; too much functionality may add maintenance burden for a tiny team. Actual hosting cost unknown. |
| [pretix](https://github.com/pretix/pretix/tree/e4b29f56a47788a52a606bdb5c71380b20da36f8) | [README](https://github.com/pretix/pretix/blob/e4b29f56a47788a52a606bdb5c71380b20da36f8/README.rst) describes event ticketing, self-hosting documentation and release/stability caveats for master. Root includes deployment and test facilities. | [AGPLv3 with additional terms](https://github.com/pretix/pretix/blob/e4b29f56a47788a52a606bdb5c71380b20da36f8/LICENSE); special conditions vary with SaaS/third-party service use. **Not cleared for copying or adapting.** | Useful reference for registration/ticketing and failure flows; potentially far beyond the proposed scope. Deployment/support costs unpriced. Do not blindly fork; a license compatibility review is required. |
| [Open Event Server](https://github.com/fossasia/open-event-server) | Existing open-source event management reference. | Not inspected in this snapshot. | Its GitHub repository is archived as of this check; not a preferred actively maintained starting point. |

Repositories above were checked through publicly accessible GitHub metadata and the indicated repository documentation/license files. This **does not verify live accessibility, production reliability, licensing of every asset, dependency advisories or operational costs**. No reference code was executed.

## The simpler alternative must also be evaluated

For a student team, compare:
1. Static event pages plus **external registration and meeting services**, after verifying their retention policies, quotas and terms. Lowest custom code burden, but vendor dependence and weaker control of data.
2. One small application with a relational database, owner-only administration, registration confirmation and no self-hosted video. Better control, but persistent storage, notifications, backup, abuse prevention and deployment must fit verified quotas.
3. Full event management platform such as Indico. More mature event features, but higher migration, configuration and operational complexity.

Do not make a selection based on initial setup ease alone. Research **dated provider quotes**, registration data volume, notifications, data protection, domain and transport options, peak workshop registration spikes, service suspension rules, restoration, and who will administer the website. If the $0 monthly bound cannot be met in a verified public plan, report it as a conflict rather than invent a free tier.

### Proposed owner-facing explanation (not a completed application)

The visitor sees a workshop list with clear dates, location/online status and available places. Clicking a workshop opens details and a simple registration form. The user is told the truth about whether their registration is saved, whether it is merely queued, or whether the service is unavailable. Admins see registrations and can correct or cancel workshops; visitors cannot see other visitors' private details. The live workshop is hosted on an external service, **not a self-built video streaming stack**, unless there is a separately costed technical reason.

The first deliverable should be one demonstrable core journey, with tests for duplicate submissions, authorization, retention, missing-network errors and persistence after refresh. A screenshot with attractive colors is useful for design review, but not an acceptance test.

## Architectural consequences from supplied study material

The supplied software architecture notes emphasize choosing a few **architecturally significant characteristics**, evaluating cohesion/coupling and avoiding entity-shaped modules, and assigning availability/scale to actual deployment boundaries. The decision here prioritizes budget, a verifiable registration record, modest operational burden and mobile/RTL accessibility rather than prematurely splitting registrations, users and workshops into microservices. A single deployable application is a **hypothesis to validate**, not a proven solution without price and usage evidence.

The operational and security checks come from [the previously synthesized source notes](book-insights.md); actual applicability depends on the eventual selected stack and deployment.
