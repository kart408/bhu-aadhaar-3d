# Phase 15 — Durable approved-property storage

Date: 2026-09-26

## Outcome

Registrar approval now creates a durable row in SQLite's
`registered_properties` table. The stored snapshot contains:

- proposal ID and parent ULPIN;
- property type, unit and address;
- exact six-coordinate XYZ bounds;
- manual or point-cloud geometry source and provenance;
- registration basis;
- approval time and registrar label.

The proposal also changes to `APPROVED`, reports `registration_stored: true`,
and receives a `REGISTERED_PROPERTY_STORED` event in the chained audit history.
These writes occur in the same database transaction, so partial approval is not
left behind if storage fails.

The ULPIN model endpoint merges stored approved properties into the matching 3D
building. Its public feature excludes applicant identity but includes the unit,
XYZ geometry, source, approval time and administrative-waiver basis.

## Verification

Tests confirm that a waived approval creates exactly one stored registration,
retains its bounds and basis, appears in the matching parent model, and appends
the storage audit event.
