# 100-error matrix: mistake -> alternative -> evidence

The numbering preserves the supplied list. These are review prompts, not a claim that AI always makes these mistakes. Source IDs resolve in [sources.md](sources.md). Alternatives/checks are original synthesis; references support principles, not every proposed test. Apply with context and record pass/fail/N/A plus evidence.

## Planning and architecture

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 1 | Coding without requirements | Define actors, outcomes, scope and acceptance before pages | Trace each launch feature to a requirement and acceptance scenario | A,D,G |
| 2 | Disorganized structure | Group cohesive capabilities with named owners and dependency boundaries | Follow one change through files; check for cross-boundary imports | A,D,G |
| 3 | Monolithic components | Split distinct responsibilities through small explicit interfaces | Change a domain rule without editing presentation/persistence details | A,D,G |
| 4 | Code duplication | Share genuinely identical policy; avoid abstracting unrelated similarities | Modify one shared rule and exercise every caller | A,D,G |
| 5 | Unnecessary complexity | Choose minimal dependencies from measured requirements | Explain purpose and resource/maintenance cost of each major dependency | A,D,G |
| 6 | Non-scalable design | Model load and growth; define capacity and revisit triggers | Load representative data and inspect tail latency and saturation | A,D,G |
| 7 | Mixed layers | Keep UI/transport separate from trusted domain and persistence behavior | Verify browser modules cannot import privileged database code | A,D,G |
| 8 | Inconsistent architecture | Record a supported pattern and justify local exceptions | Review comparable flows against documented boundaries | A,D,G |
| 9 | Ignoring existing code | Read behavior, tests and conventions before targeted improvement | Compare required behavior before/after and run relevant regressions | A,D,G |
| 10 | Reinventing critical primitives | Use maintained security/payment/accessibility implementations | Review library suitability, maintenance and configuration; test integration | A,D,G |

## Design and user experience

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 11 | Generic repetitive design | Choose task/content-led composition and explicit brand rationale | Compare two directions with the same real content and tasks | U |
| 12 | Excessive effects | Use motion/elevation only to convey relationships or feedback | Remove each effect and assess benefit plus constrained-device trace | U |
| 13 | Weak hierarchy | Establish heading, content and action roles | Have a reviewer identify primary task and next action quickly | U |
| 14 | Clutter | Prioritize critical content and disclose secondary detail progressively | Complete the main task without unrelated distractions | U |
| 15 | Inconsistent spacing | Use a small spacing scale and grouping rules | Inspect comparable components across routes and widths | U |
| 16 | Inconsistent visual language | Use shared semantic tokens and documented component variants | Compare buttons, headings, focus and states across pages | U |
| 17 | Fake interactions | Implement promised outcomes across required layers | Trigger every control and verify real navigation or durable effect | U |
| 18 | Missing UI states | Specify loading, empty, validation, denied, conflict and outage states | Force each state with controlled data/network responses | U |
| 19 | Confusing navigation | Organize destinations around user tasks and clear labels | Observe representative users reaching key tasks and returning | U |
| 20 | No feedback | Report pending and actual outcomes with recovery actions | Submit slow/failing/successful operations and inspect announcements | U |

## Responsiveness and accessibility

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 21 | Desktop-only layout | Adapt hierarchy and controls to narrow screens | Exercise core journeys on touch viewport and real device if available | W,U |
| 22 | Fixed overflow widths | Use fluid layout and constrained responsive sizing | Check reflow at 320 CSS pixels where applicable and enlarged text | W,U |
| 23 | Overlapping content | Use intrinsic sizing and test long real content | Inspect long labels, errors, zoom and breakpoint transitions | W,U |
| 24 | Broken Arabic RTL | Use language/direction, logical CSS and mixed-text isolation | Test Arabic/English dates, prices, URLs and keyboard order | W,U |
| 25 | Poor contrast | Assign semantic colors and verify actual pairings | Measure text and applicable non-text contrast in all states | W,U |
| 26 | Small touch targets | Meet applicable WCAG target-size rules and comfortable spacing | Measure targets/spacing and try primary actions by touch | W,U |
| 27 | Mouse-only interaction | Use semantic controls and visible keyboard focus | Complete all core tasks without a mouse | W,U |
| 28 | Unlabeled fields | Associate persistent labels, help and errors | Inspect accessible names and screen-reader field announcements | W,U |
| 29 | Missing image alternatives | Describe meaningful images; empty alt for decorative images | Review image purpose and accessible reading experience | W,U |
| 30 | Broken dialog focus | Use appropriate focus placement, containment and return | Open, navigate, dismiss and reopen using keyboard/screen reader | W,U |

## Frontend and React

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 31 | Redundant state | Store minimal source state; derive calculable values | Update inputs and assert derived views remain consistent | R |
| 32 | Unnecessary effects | Use event handlers/derived values; effects synchronize external systems | Review each effect purpose and dependent update behavior | R |
| 33 | Unstable keys | Use stable identity for mutable/reorderable lists | Insert/delete/reorder and verify inputs stay with correct records | R |
| 34 | Direct state mutation | Update through supported immutable state patterns | Verify prior snapshots unchanged and expected rerender occurs | R |
| 35 | Excessive rerenders | Profile first, localize state, memoize only justified work | Measure representative interaction before/after optimization | R |
| 36 | Request races | Cancel or ignore superseded responses by request identity | Resolve earlier request last and assert newest view stays correct | R |
| 37 | Resource leaks | Pair external subscriptions/listeners with lifecycle cleanup | Mount/unmount repeatedly and inspect duplicate handlers/resources | R |
| 38 | Hydration mismatch | Keep server/client initial output deterministic | Inspect production hydration logs with locale/time variations | R |
| 39 | Unneeded client code | Render static/server work outside interactive client boundaries | Inspect production route bundles and browser-only requirements | R |
| 40 | Lost input state | Preserve intentional component identity and draft lifecycle | Navigate/update unrelated state and verify drafts persist as contracted | R |

## Backend and API

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 41 | Trusting frontend validation | Validate and enforce permissions server-side | Bypass UI and send invalid/unauthorized requests directly | O,S,G |
| 42 | Incomplete validation | Define schemas, bounds, allowed fields and semantic rules | Send wrong types, boundary values and forbidden fields | O,S,G |
| 43 | False HTTP success | Use consistent status and error contracts matching outcome | Assert response status/body and persisted state for failures | O,S,G |
| 44 | Unbounded list responses | Enforce page limits with stable ordering | Request oversized pages and inspect payload/query bounds | O,S,G |
| 45 | No dependency timeout | Use explicit deadlines and bounded cancellation | Hold dependency response and measure controlled termination | O,S,G |
| 46 | Blind retries | Retry only eligible failures with bounded backoff/jitter | Simulate repeated failures and inspect attempts and duplicate effects | O,S,G |
| 47 | No idempotency | Atomically scope/deduplicate operations with payload matching | Replay/concurrently submit same key; reject changed payload | O,S,G |
| 48 | Leaking internal errors | Return safe messages and restricted correlated diagnostics | Cause internal failures and inspect response/log redaction | O,S,G |
| 49 | Inconsistent API | Document field names, schemas and compatibility policy | Run consumer contract checks across related endpoints | O,S,G |
| 50 | Assuming providers succeed | Define outage, reconciliation and degradation behavior | Fail provider calls and verify truthful state and recovery | O,S,G |

## Security

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 51 | Exposed API secrets | Keep privileged keys server-side and rotate exposures | Inspect bundle, tracked files and logs without exposing key values | H,M,O,V |
| 52 | Weak action authorization | Deny by default and check action/role on server | Ordinary user calls administrative endpoint directly | H,M,O,V |
| 53 | IDOR | Scope object queries/actions to trusted owner/tenant policy | User A reads/updates/deletes/exports user B records | H,M,O,V |
| 54 | SQL injection | Use parameterized queries and safe query construction | Inspect query sinks and exercise malicious input in authorized tests | H,M,O,V |
| 55 | XSS | Encode by context; sanitize permitted HTML; layer CSP | Exercise untrusted text/HTML/URL inputs and verify no execution | H,M,O,V |
| 56 | CSRF where applicable | Protect ambient-credential mutations with appropriate controls | Cross-origin forged mutation fails while valid request works | H,M,O,V |
| 57 | Unsafe passwords | Use maintained adaptive password hashing with current parameters | Inspect stored format/config and verify no plaintext or fast hashes | H,M,O,V |
| 58 | Unsafe uploads | Bound, inspect and isolate uploads with access controls | Try oversized/mismatched/active files and unauthorized retrieval | H,M,O,V |
| 59 | Unsafe CORS | Allow only required origins and credential combinations | Test approved/unapproved browser origins; separately test auth | H,M,O,V |
| 60 | Vulnerable dependencies | Lock, audit and remediate supported dependencies | Review advisories and applicability; document unresolved risk owner | H,M,O,V |

## Performance and resources

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 61 | Oversized images | Serve appropriate responsive variants and compression | Compare rendered dimensions, selected source and transfer | P |
| 62 | Layout shift from media | Reserve dimensions/aspect ratio before load | Inspect layout-shift trace under cold slow load | P |
| 63 | Excessive JavaScript | Prefer native/server behavior and route-specific client code | Measure compressed route JS and execution on constrained CPU | P |
| 64 | No code splitting | Defer heavy route/feature code without creating waterfalls | Inspect actual chunks and network critical path | P |
| 65 | Sequential independent requests | Parallelize independent reads with bounded concurrency | Inspect waterfall and quota/saturation impact | P |
| 66 | No caching | Cache suitable stable data with explicit freshness policy | Repeat requests and verify hit behavior and reduced cost | P |
| 67 | Incorrect/private cache | Scope keys and invalidation to data ownership and freshness | Switch users/tenants and mutate data; verify isolation and updates | P |
| 68 | Heavy fonts | Load only required families, weights and script subsets | Inspect font transfer and Arabic fallback/character coverage | P |
| 69 | Expensive rendering effects | Use measured low-cost motion and static/reduced alternatives | Trace scrolling/interactions and inspect long tasks/render work | P |
| 70 | Eager noncritical loading | Defer below-fold/optional assets; prioritize critical content | Inspect initial requests and ensure LCP media is not delayed | P |

## Database and information

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 71 | Missing indexes | Index measured high-value query paths | Inspect plans and p95 latency on representative cardinalities | D |
| 72 | N+1 queries | Batch/join/preload related data within payload bounds | Count queries while increasing record count | D |
| 73 | Invalid relationships | Model domain cardinality and enforce referential constraints | Attempt orphaned/invalid references and exercise lifecycle deletes | D |
| 74 | Partial dependent writes | Use correctly scoped transactions for atomic invariants | Inject mid-operation failure and assert no partial state | D |
| 75 | Concurrent corruption | Select atomic updates/locking/versioning/isolation from invariant | Stress simultaneous writes and assert preserved invariant | D |
| 76 | No uniqueness constraint | Enforce domain uniqueness in the database | Submit concurrent duplicates and verify one allowed record | D |
| 77 | Timezone confusion | Store instants correctly and retain scheduling timezone intent | Test boundary dates, UTC conversion and DST where applicable | D |
| 78 | Unsafe schema change | Use compatible phased migration and backfill plan | Run old/new versions against migration and inspect locks/data | D |
| 79 | Unverified backup | Protect backups and rehearse restore against RPO/RTO | Restore isolated copy and verify integrity and measured recovery | D |
| 80 | Excess personal data | Minimize collection and define retention/deletion | Inventory fields/logs/backups and execute applicable deletion flow | D |

## Testing and reliability

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 81 | Missing logic tests | Test important business invariants with focused unit cases | Exercise boundaries and confirm tests detect wrong outcomes | T,C,G |
| 82 | Render-only validation | Validate observable behavior through necessary layers | Complete journey and verify database/API result after refresh | T,C,G |
| 83 | No E2E journeys | Cover a small set of critical full user outcomes | Run isolated browser journey against real test persistence | T,C,G |
| 84 | Happy-path-only tests | Include invalid, boundary, denial, duplicate and failure cases | Map feature failure states to exercised scenarios | T,C,G |
| 85 | No permission tests | Test role/object/tenant policies with distinct identities | Attempt cross-user, cross-tenant and privilege escalation paths | T,C,G |
| 86 | Ignoring bad networks | Test latency, timeout, disconnect and ambiguous completion | Interrupt writes and verify recoverable, truthful UI | T,C,G |
| 87 | Nonisolated tests | Create independent fixtures and cleanup owned data | Run reordered/parallel tests without inherited state | T,C,G |
| 88 | No regression protection | Add a behavior test for a meaningful reproduced defect | Prove failure before fix and pass after without implementation coupling | T,C,G |
| 89 | No diagnostic logs | Use redacted structured logs and correlation | Investigate controlled error from request to cause without secrets | T,C,G |
| 90 | No monitoring | Monitor user impact, tail latency and saturation with owned alerts | Trigger safe alert condition and verify routing/runbook usefulness | T,C,G |

## Deployment, maintenance and SEO

| ID | Failure | Constructive alternative | Observable verification | Sources |
| --- | --- | --- | --- | --- |
| 91 | Development-only verification | Build and exercise production artifact | Run production build/start and core smoke journey | N,Q,G |
| 92 | Missing configuration | Validate required env schema and document secret setup | Start with absent/invalid required config and verify safe failure | N,Q,G |
| 93 | Development URLs in release | Use validated environment-aware URL construction | Scan artifact and exercise deployed links/provider callbacks | N,Q,G |
| 94 | Missing error routes | Provide useful not-found/server-failure behavior and statuses | Request unknown route and force controlled server error | N,Q,G |
| 95 | Accidental indexing block | Set indexing by environment and content sensitivity | Inspect production robots/meta/headers for public routes | N,Q,G |
| 96 | Missing metadata | Provide page-specific title/description and sharing data | Inspect rendered public pages and link preview metadata | N,Q,G |
| 97 | Missing discovery sitemap | Supply sitemap when useful for public indexable content | Validate URLs/status/canonical consistency; N/A for private-only apps | N,Q,G |
| 98 | Incorrect canonical | Point to intended canonical public URL | Inspect aliases/query variants and canonical output | N,Q,G |
| 99 | No rollback plan | Retain compatible safe release and separate data recovery plan | Rehearse rollback trigger/procedure without destructive data reversal | N,Q,G |
| 100 | Incomplete documentation | Document run/config/decisions/tests/operations and known gaps | Fresh maintainer follows setup and verifies core journey | N,Q,G |
