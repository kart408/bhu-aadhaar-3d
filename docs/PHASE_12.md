# Phase 12 — Tamper-evident audit history

Date: 2026-09-26

## Outcome

Every durable workflow transition now appends an audit event:

- `PROPOSAL_SUBMITTED`;
- `SPATIAL_VALIDATION_COMPLETED`;
- `REGISTRAR_DECISION_RECORDED`.

Each event stores the SHA-256 hash of the preceding global event, its canonical
JSON detail, proposal ID, event type and UTC timestamp. This forms an ordered
hash chain. Editing, deleting, inserting or reordering a stored event breaks
verification for that event or a later link.

`GET /api/proposals/{id}/audit` returns the proposal's events and the result of
verifying the complete database chain. The registrar console shows durable event
timestamps, hash prefixes and the current chain status.

## Verification

The automated tamper test submits and rejects a proposal, verifies the valid
three-event chain, modifies the first event directly in SQLite, and confirms
that verification fails.

```bash
.venv/bin/python -m unittest tests.test_registry -v
```

## Security boundary

A hash chain is tamper-evident, not tamper-proof. An attacker with database and
application-key access could recompute every later hash. Production should
periodically anchor signed chain heads in an independently controlled system,
use authenticated officer identities, restrict database writes, and export
append-only audit records to separate retention infrastructure.
