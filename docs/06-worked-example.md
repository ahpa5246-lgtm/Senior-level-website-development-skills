# Worked example: a limited-capacity class reservation

This invented example demonstrates the framework; it is not a tested application or code copied from a book.

## Contract

A signed-in student reserves one seat in a class. The outcome is a durable reservation with an identifier, visible after refresh. A student cannot reserve twice; capacity cannot become negative. Instructors may view students only for classes they manage. Public users may browse class descriptions without receiving student details.

UI states: browsing, no classes, signing in, submitting, confirmed, already reserved, full, forbidden and temporarily unavailable. Disable duplicate clicks for usability, but enforce duplicates on the server. Every tab has a real route/query: upcoming classes, my reservations and instructor management with role checks.

## Small architecture

One deployable application with catalog and reservation modules and a relational database. Public descriptions may be rendered statically/server-side; writes use trusted endpoints. A maintained authentication provider/library supplies identity. No queue is required for the core reservation; optional email can be added independently with a clear delivery contract.

## Operation

1. Validate class ID and request schema; derive student ID from authenticated identity.
2. Check eligibility and class state on the server.
3. In one short DB transaction claim the operation key, atomically decrement remaining capacity only if it is positive, and insert the reservation with unique `(class_id, student_id)` and relational constraints. If an insertion fails, the capacity update must roll back. Scope the idempotency key to actor and operation; reject a changed payload.
4. Commit before reporting confirmation. A timed-out client can query/replay the same operation safely. Keep idempotency lifecycle explicit.
5. If sending email is required, persist an outbox event within the transaction and have a worker retry safely. Email failure must not falsify reservation status.

This outline requires implementation-specific isolation/locking review and contention tests; pseudocode is not proof of correctness.

## Evidence plan

| Risk | Acceptance scenario |
| --- | --- |
| Fake persistence | Reserve, refresh, sign out/in, observe the same reservation |
| Overselling | Concurrently attempt more reservations than seats; assert capacity and successful count |
| Duplicate write | Replay the same key; concurrent repeat; new key for same student; assert one reservation |
| IDOR | Student A requests student B's reservation through the API; deny without data leak |
| Tenant/role bypass | Unrelated instructor queries roster/export; deny |
| Dependency failure | DB unavailable/timeout; no false confirmation and preserved input |
| Accessibility | Complete reservation with keyboard and screen-reader announcement |
| Low-end cost | Cold load and submit under recorded profile; inspect JS, transfer and main-thread work |
| Deployment | Production build, compatible migration, smoke journey and safe rollback |

Design direction: task-led class list with date/capacity information, a clear reserve action, review where commitment warrants it, and confirmation with next steps. Semantic accent colors support action/status; no shader or animation is needed to communicate a seat reservation.
