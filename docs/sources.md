# Source ledger and attribution boundaries

Research date: 2026-10-14. Supplied books were extracted locally for targeted reading; eight images were visually inspected. Extraction is an access method, not evidence of exhaustive reading. No full book text or image is published. Book locations below use chapter/section names; printed pages and PDF indices differ. Verify runtime/library settings against current official documentation before implementation.

## Supplied material

| ID | Source and edition observed | Locations used | Role and limitation |
| --- | --- | --- | --- |
| D | Designing Data-Intensive Applications, 2nd edition, Martin Kleppmann and Chris Riccomini | Reliability/scalability/maintainability; data models; encoding/schema evolution; replication; sharding; chapter 8 Transactions, including isolation anomalies and serializability | Data guarantees and trade-offs; not a frontend style guide |
| G | Building Secure and Reliable Systems, Google/O'Reilly, 2020 | Chapters 5 Design for Least Privilege (printed p61 onward), 6 Design for Understandability (p89 onward), 8 Design for Resilience (p143 onward), 9 Design for Recovery (p183 onward), 13 Testing Code (p271 onward); incident/recovery discussions | Security and reliability across design and operation; Google-scale examples need proportional adaptation |
| H | Web Application Security, Andrew Hoffman, 2nd edition, January 2024 | Chapters 21 Secure Application Architecture (p237), 24 Threat Modeling Applications (p277), 25 Reviewing Code for Security (p289), 28 XSS defenses (p319), 29 CSRF defenses (p331), 31 Injection defenses (p343), 32 DoS defenses, 35 Dependencies, 36 Business Logic | Attack surface and layered mitigation; historical code is not a current framework template |
| M | API Security in Action, Neil Madden, Manning; EPUB metadata is unreliable for publication date | Chapter 1 goals/threats; identity/authorization discussions; chapter 7 OIDC token purpose; chapter 9 capability permissions; chapter 11 service-to-service authentication | API authority, token boundaries and audit; modern provider guidance must supersede outdated flows |
| A | Supplied chapter_1 through chapter_8 PNG study summaries | Architecture definitions; trade-offs; modularity; quality attributes; identification/measurement; architecture quantum; component partitioning | Secondary summaries, not original full book chapters. Chapter 7 explicitly names Fundamentals of Software Architecture; authorship/edition of the summary set not established |

## Official web references checked

| ID | Reference | Principle used |
| --- | --- | --- |
| R | [React: You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect) | Derived state and effects for external synchronization |
| O | [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) | Endpoint access control, validation, safe errors, bounded methods and CORS |
| V | [OWASP ASVS](https://owasp.org/projects/asvs) | Verification requirements; page reports stable 5.0.0 when checked; select/pin actual requirement versions |
| S | [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests) | Provider-specific replay semantics; generic operation design remains a synthesis |
| W | [WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/) | Applicable contrast, keyboard, reflow, focus and target-size criteria |
| U | [GOV.UK functional color](https://design-system.service.gov.uk/styles/colour/), [GOV.UK check answers](https://design-system.service.gov.uk/patterns/check-answers/), [Carbon data tables](https://www.carbondesignsystem.com/building-blocks/core/components/data-table), [Adobe Spectrum typography](https://spectrum.adobe.com/page/typography/) | Semantic color, task review, tabular data, type hierarchy; synthesized direction families are not endorsed presets |
| P | [Google Web Vitals](https://web.dev/articles/vitals) | LCP, INP, CLS, p75 and lab/field distinction; local byte budgets are not Google standards |
| T | [Playwright best practices](https://playwright.dev/docs/best-practices) | User-visible outcomes, isolated tests and robust interaction tests |
| C | [GitHub review of AI-generated code](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) | Review and verify generated suggestions rather than assuming correctness |
| N | [Next.js production checklist](https://nextjs.org/docs/app/guides/production-checklist) | Production build/configuration/performance considerations; applicable only to selected stack |
| Q | [Google JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) | Public content rendering, crawling and indexing behavior |
| SO | [Stack Overflow 2025 AI survey](https://survey.stackoverflow.co/2025/ai) | Context on developer frustrations; not proof of defect frequency for these 100 items |

The user's 66% survey figure concerns respondents' frustration with solutions that are almost correct. It must not be restated as “66% of AI websites are defective” or as a representative defect rate. The framework does not depend on that statistic.

## Evidence discipline

A source-derived principle is distinct from our recommended implementation and from a measured result. A book explaining concurrency does not prove a proposed reservation transaction is correct; that requires database-specific review and tests. A design system does not validate an invented palette. A current reference does not ensure future settings remain current. Re-check versions and security parameters when applying the framework.
