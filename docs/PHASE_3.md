# Phase 3 — Minimal interactive 3D viewer

Date: 2026-09-26

## Outcome

A zero-dependency browser application displays the Phase 2 volumes using an
isometric canvas renderer. It intentionally avoids a framework and external map
SDK until the user flow is proven.

Features:

- apartment, basement and underground utility rendering;
- type and floor filters;
- click-to-inspect proposed 3D ULPIN, height, area and volume;
- rejected spatial conflicts rendered in red;
- conflict reason and out-of-parcel error display;
- responsive desktop/mobile layout.

## Run

From the project root:

```bash
python3 scripts/build_demo.py
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/viewer/>.

Opening `index.html` directly will not work because browsers block local `fetch`
requests. Use the local HTTP server command above.

## Acceptance demo

1. View all registered volumes as one tower.
2. Filter to Floor 3 and select Unit 302.
3. Read its proposed identifier and volumetric measurements.
4. Select “Rejected proposals”.
5. Click the red duplicate and see its Unit 302 conflict.
6. Click the red outside unit and see `OUTSIDE_PARENT_PARCEL`.

## Deliberate limitation

This phase proves interaction and storytelling, not geographic accuracy. A later
phase may replace the renderer with MapLibre or Cesium after the core workflow
and visual hierarchy are accepted.

