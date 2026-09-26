# Phase 8 — Property intake and automatic box generation

Date: 2026-09-26

## Outcome

The citizen-facing intake converts ordinary property details into a reviewable
3D proposal. The shop-owner example is pre-filled at `apps/intake/`.

The MVP pipeline:

1. validates the existing 14-digit parent ULPIN;
2. resolves the building to a demo longitude/latitude anchor;
3. resolves shop `G-12` to a local building-plan offset;
4. converts owner-supplied feet to metres;
5. derives the Z base from the selected floor;
6. creates axis-aligned `[xmin, ymin, xmax, ymax, zmin, zmax]` bounds;
7. computes area, volume, centroid and a deterministic proposal reference.

An address is only a building anchor; it cannot locate a shop within that
building. The demo therefore makes the unit-directory lookup explicit. In a
production flow that lookup must come from a sanctioned floor plan, indoor
survey, BIM model, or a registrar-controlled placement step.

## Run

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/intake/> and select **Generate 3D property**.

## Next geometry mode

The disabled survey import represents Mode 2. A point-cloud pipeline would
detect horizontal Z clusters for floor slabs, segment the selected unit's walls,
and return geometry with accuracy, datum, acquisition time, and survey provenance.
It should feed the same review and registrar-validation contract as Mode 1.
