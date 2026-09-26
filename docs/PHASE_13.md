# Phase 13 — ULPIN-isolated building viewer

Date: 2026-09-26

## Outcome

The 3D viewer is now ULPIN-first. A person enters a 14-digit parent ULPIN and the
backend returns only the matching parcel's model through:

```text
GET /api/parcels/{ulpin}/model
```

For the synthetic demo ULPIN `12345678901234`, the response contains 11 validated
registered volumes and two rejected proposals. It includes no owner or applicant
identity. The UI reports total registered volume, lets the user filter and inspect
individual height bands, and explains duplicate-volume and outside-parcel
rejections.

**Show LiDAR points** overlays the 136-point synthetic Shop G-12 scan in the same
XYZ projection. This connects the advanced survey source to visible 3D geometry;
the intake application separately uses those points to detect floor and ceiling
surfaces and generate a proposal volume.

## Run

```bash
.venv/bin/python scripts/run_registry_server.py
```

Open <http://127.0.0.1:8000/apps/viewer/> and enter `12345678901234`.

## Registration and privacy boundary

A ULPIN lookup is not authentication and cannot establish that the visitor owns
the parcel. The public response therefore exposes synthetic geometry and
registration facts only. Real owner records require authenticated, authorized
access. Likewise, LiDAR-derived geometry remains a proposal until server-side
parcel containment, overlap, source-quality, officer review and durable audit
requirements pass.
