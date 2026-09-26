# Phase 2 — Minimal demo geometry

Date: 2026-09-26

## Outcome

The project now has one clearly labelled synthetic parcel containing:

- four floors with two units per floor;
- two basement parking volumes;
- one underground utility volume;
- one deliberately overlapping proposed unit;
- one deliberately out-of-parcel proposed unit.

The geometry engine performs exact intersection checks for the rectangular
solids used in this MVP. Touching walls and floors are permitted; positive shared
volume is a conflict.

## Build generated data

```bash
python3 scripts/build_demo.py
```

Outputs:

- `data/generated/demo_volumes.geojson`
- `data/generated/validation_report.json`

## Scope boundary

The seed uses local metre coordinates and relative heights. Its WGS84 map anchor
and conversion are for visualization only. Nothing in this dataset is an
official parcel, official ULPIN, survey result or ownership record.

Arbitrary polygons and legal 3D solids remain future work. The current engine is
intentionally honest: its result is exact for axis-aligned rectangular volumes,
not for every cadastral geometry.

## Phase 2 acceptance criteria

- All 11 registered volumes fit inside the parent parcel.
- Registered volumes do not overlap.
- Adjacent units may share faces without being rejected.
- The planted duplicate of Unit 302 is rejected as a spatial conflict.
- The planted outside unit is rejected for leaving the parent parcel.
- Every registered volume receives a valid proposed 3D identifier.
- A GeoJSON feature collection and machine-readable validation report are built.

