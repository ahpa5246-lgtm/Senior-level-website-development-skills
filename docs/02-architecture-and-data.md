# Architecture and data: choose boundaries from change and invariants

Basis: supplied architecture notes chapters 1-8; DDIA 2nd edition, reliability/scalability discussions, encoding, replication, sharding and transactions. Recommendations below are synthesis, not verbatim book rules.

## Match architecture to the workload

| Situation | Starting option | Reason to reconsider |
| --- | --- | --- |
| Public content, no shared writes | Static generation and ordinary links | Frequent personalized content or trusted writes |
| Small authenticated product | One deployable application, domain modules, relational DB | Proven independent scaling, failure isolation or team ownership needs |
| Long-running media/report work | App plus bounded worker and durable job store | Queue age/throughput require independently scaled workers |
| Multiple teams with distinct domains | Independently owned services where justified | Distributed consistency and operational costs exceed autonomy gains |

Organize by cohesive capabilities such as reservations, billing and catalog. Within a capability separate transport/UI, use-case orchestration, domain decisions and persistence adapters when those boundaries solve real coupling. Do not build a directory or class for every table. Keep shared code small and stable; duplication may be safer than a false abstraction between unrelated domains.

Example structure for a growing transactional application (adapt to the framework, do not copy mechanically):

```text
src/modules/reservations/{transport,application,domain,persistence}
src/modules/catalog/
src/platform/{database,identity,observability}
tests/{integration,e2e}
migrations/
docs/{decisions,runbooks}
```

## Express invariants at the trusted boundary

Examples: a tenant may only read its records; remaining inventory cannot go below zero; a provider payment event may affect an order once. Write these as testable conditions. Database constraints are a final integrity layer: foreign keys, uniqueness and appropriate checks protect against all callers, including concurrent requests.

A transaction guarantees only what its database, scope and isolation level actually implement. Wrapping read-modify-write in a transaction does not automatically prevent lost updates or write skew. Choose atomic conditional updates, locks, optimistic versions or serializable isolation from the invariant; exercise contention and handle retryable conflicts within a bounded policy.

## Query and growth policy

Use representative query plans and cardinalities before adding indexes. Indexes consume storage and write work. Batch related reads to avoid N+1. Pagination needs stable ordering and a tie-breaker; cursor pagination is useful for large/changing datasets, while offset pagination can be sufficient for small administrative lists. Enforce maximum page size server-side.

Use replicas only after defining tolerated staleness. Read-your-writes may require primary reads or another explicit strategy. Sharding brings cross-partition query and transaction costs; do not introduce it without evidence that simpler capacity measures fail.

## External effects are not local transactions

Do not hold a DB transaction open while calling a slow payment/email service. For reliable DB + message coordination, consider a transactional outbox and an idempotent consumer. Define retry bounds, deduplication lifetime and dead-letter/reconciliation handling. Outbox delivery alone does not provide exactly-once effects at the destination.

## Evolution and recovery

Use expand -> deploy compatible code -> bounded backfill -> verify -> contract. Old and new app versions may run together. Record lock/runtime implications and rollback compatibility. Reversing a migration may destroy new data; sometimes roll-forward is safer. Keep encrypted access-controlled backups and rehearse restoration against explicit RPO (tolerable data loss) and RTO (recovery time).

Store instants in UTC with timezone-aware representation. Preserve the user's IANA timezone and local intent for recurring schedules; UTC alone does not encode “9am every day” through daylight-saving changes. Minimize personal data and define retention/deletion including replicas, logs and backups.

## Correcting the supplied summary shortcuts

- A shared database can create deployment and failure coupling; it does not universally prove every service is one architectural quantum. Evaluate schema ownership, access and runtime dependencies.
- Async work can reduce synchronous coupling, but queues, backlog, schemas and consumers still introduce dependencies and failure modes.
- Availability multiplication assumes particular independent serial dependencies; correlated failures, fallback and retries change the model.
- Coupling/cohesion metrics and complexity thresholds are diagnostic tools, not universal pass/fail scores.
- Security does not always decrease performance, and consistency/availability trade-offs require a stated failure model. Do not treat arrows in a summary image as physical laws.
