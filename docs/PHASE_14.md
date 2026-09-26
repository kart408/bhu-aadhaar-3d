# Phase 14 — Simplified administrative registrar

Date: 2026-09-26

## Outcome

The registrar console now contains only the submitted registration information
needed for the requested administrative demo:

- parent ULPIN;
- address;
- property type and unit;
- applicant label;
- manual or LiDAR geometry source;
- a review confirmation and approval action.

Prepared geometry scenarios, building-volume matching, parcel-length comparison,
the spatial-validation button and the rejection action were removed from the UI.
The registrar can approve an incoming request even when the advisory backend
geometry result reports a conflict.

## Explicit waiver

Unchecked geometry is not silently described as validated. An approval that has
spatial findings must include a waiver reason. The durable decision event records:

```text
geometry_check: WAIVED
override_reason: Administrative registration requested; building-length and
                 volume matching were not applied.
```

Approval without that reason remains blocked at the API. This preserves an honest
audit record while providing the simplified one-click workflow.

## Scope warning

This mode is suitable only for demonstrating administrative workflow. Real 3D
cadastral registration should not waive parcel containment, overlap, survey
accuracy, title-document and authorized-officer checks.
