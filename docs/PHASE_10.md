# Phase 10 — Citizen-to-registrar proposal handoff

Date: 2026-09-26

## Outcome

The intake and registrar applications now form one continuous prototype flow:

1. the owner generates geometry from measurements or the synthetic point cloud;
2. the intake creates a versioned `BHU3D_PROPERTY_PROPOSAL_V1` record;
3. **Send to registrar validation** stores the pending record in same-origin
   browser storage and opens the registrar console;
4. the registrar automatically selects the incoming proposal;
5. existing parcel-containment and positive-volume intersection checks run;
6. approval or rejection clears the pending record.

The proposal carries the parent ULPIN, applicant and property labels, six metric
bounds, geometry-source classification, and provenance. Input is schema-checked
again when the registrar loads it. Invalid or corrupted stored data is discarded.

## Demonstration

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/intake/>, generate Shop G-12, and select **Send
to registrar validation**. Select **Run spatial validation** in the registrar.

G-12 deliberately overlaps the registered ground-floor `UNIT-101` in the shared
synthetic parcel, so the correct decision is rejection. This shows that geometry
generation does not bypass cadastral conflict checks.

## Architecture boundary

Browser storage is a transparent hackathon transport, not a submission system.
Production requires an authenticated API, durable database, applicant consent,
role-based access, encryption, malware/file scanning, immutable audit events,
workflow status, and server-side repetition of every validation. Client-provided
geometry and identity data must never be trusted merely because the UI accepted it.
