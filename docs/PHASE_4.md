# Phase 4 — Registrar validation workflow

Date: 2026-09-26

## Outcome

The registrar simulation turns the geometry engine into a three-step operational
story:

1. select a parent parcel;
2. review and spatially validate a proposed volume;
3. approve valid geometry or record a rejection.

Three prepared scenarios demonstrate a clean fifth-floor unit, a duplicate claim
over Unit 302, and a unit outside the parent parcel. Every action appears in a
session audit log.

## Run

```bash
python3 scripts/build_demo.py
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/registrar/>.

## Honest scope

Approval exists only in browser memory and disappears on refresh. This phase
does not update a database, create legal title, authenticate an officer, or
modify any government system. It proves the workflow before backend work.

## Acceptance demonstration

1. Select `PARCEL-001`.
2. Validate the clean fifth-floor unit and approve it.
3. Review another proposal and validate the duplicate Unit 302 claim.
4. Show the positive-volume intersection and rejection.
5. Validate the outside-parcel scenario and show its boundary error.
6. Point to the audit trail and legal-scope disclaimer.

