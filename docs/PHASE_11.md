# Phase 11 — Durable registry API

Date: 2026-09-26

## Outcome

The prototype now provides a same-origin HTTP server and SQLite-backed proposal
workflow. Intake submissions prefer the API and registrar decisions are written
back to it. If the apps are served by the old static server, they retain the
Phase 10 browser-storage fallback.

API operations:

- `POST /api/proposals` validates, spatially checks and persists a proposal;
- `GET /api/proposals/{id}` returns its geometry, validation and workflow state;
- `POST /api/proposals/{id}/decision` records `APPROVED` or `REJECTED`.

Approval is blocked server-side when the proposal is outside the parcel or
intersects registered geometry. Decisions are one-way and record an officer label
and UTC timestamp. Browser validation remains useful feedback but is not trusted.

## Run

```bash
.venv/bin/python scripts/build_demo.py
.venv/bin/python scripts/run_registry_server.py
```

Open <http://127.0.0.1:8000/apps/intake/>. The database is created at
`data/generated/registry.sqlite3` and is excluded from version control.

## G-12 acceptance result

The example shop is correctly rejected. Its footprint intersects `UNIT-101`, and
its owner-entered 12 ft height reaches 3.6576 m, crossing the demo storey's 3.0 m
boundary and intersecting `UNIT-201` as well. This is an explainable data-quality
finding rather than an application error.

## Security boundary

This remains a local prototype API. It has request-size and schema validation but
no authentication, authorization, TLS, CSRF protection, rate limiting, database
migrations, backup policy or tamper-evident audit log. The officer label is
client-supplied. Those controls are mandatory before any network deployment.
