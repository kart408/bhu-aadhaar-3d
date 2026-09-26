# Phase 9 — Synthetic point-cloud geometry mode

Date: 2026-09-26

## Outcome

The property intake now has a working second geometry source. **Analyze demo
scan** loads a unit-scoped synthetic survey containing 136 `(x, y, z)` points.
The browser groups nearby Z values, identifies sufficiently dense horizontal
surfaces, selects a plausible 2–6 metre floor/ceiling pair, and derives the XYZ
bounding box, dimensions, area and volume.

The result uses the same proposal rendering contract as manual measurements and
reports survey provenance, nominal accuracy and Z-detection confidence.

## Build and run

```bash
.venv/bin/python scripts/build_pointcloud_demo.py
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/intake/>, select **Analyze demo scan**, then
select **Generate 3D property**.

## Algorithm boundary

This phase demonstrates Z-coordinate analysis, not production LiDAR processing.
The input is already cropped to Shop G-12 and aligned to local building axes.
Real scans require coordinate transformation, noise/outlier removal, plane and
wall segmentation, unit selection, occlusion handling, datum control and survey
quality checks. Open3D or PDAL can provide those preprocessing stages while the
result continues to use this proposal contract.
