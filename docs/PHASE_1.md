# Phase 1 — Foundation and identifier contract

Date: 2026-09-26

## Goal

Prove the smallest risky part first: a deterministic proposed 3D identifier can
be encoded, decoded and validated without changing the official parent ULPIN.

## Verified baseline

The Department of Land Resources says that ULPIN is a 14-digit identifier based
on parcel longitude/latitude and generated using georeferenced parcel vertices.
The public overview does **not** publish:

- parcel-level ULPIN geometries for download;
- a public centre-point geohash algorithm;
- an official 3D ULPIN suffix or encoding standard.

Official overview: <https://dolr.gov.in/en/ulpin/>

Therefore this project must use these labels consistently:

- **Official:** the existing 14-digit parent ULPIN supplied by a state record.
- **Proposed prototype:** every character after the parent ULPIN.
- **Demo data:** synthetic or traced parcel/unit geometry unless its source and
  licence have been verified.

The DoLR overview is reference material, not a parcel-data API. A later data
adapter may connect to a state portal or an organizer-provided dataset.

## Corrections to the original build document

1. Do not claim that official ULPIN is a public centre-point geohash. The public
   DoLR wording refers to a formula using parcel vertices.
2. A centroid and height band do not uniquely describe an irregular unit. They
   are a compact address; the authoritative 3D boundary remains in the registry.
3. Two overlapping volumes do not necessarily produce the same identifier.
   Exact conflicts require their geometries and a spatial-intersection test.
4. An identifier alone cannot draw an exact flat offline because it does not
   contain the unit footprint or parent centroid. Offline visualization requires
   a signed/cached property payload in addition to the identifier.
5. `14 + 4 + 4 + 1` is 23 payload characters (26 when three hyphens are shown),
   not 24.
6. Height datum cannot be assumed from a sanctioned plan. Phase 2 must store the
   datum and source explicitly; demo heights are relative to an agreed building
   reference level.

## Phase 1 scope

Included:

- `encode`, `decode` and `validate`;
- deterministic half-metre quantization;
- checksum validation;
- conservative coarse overlap screening when dimensions are supplied;
- automated unit tests.

Not included:

- official ULPIN generation;
- legal ownership/title decisions;
- exact geometric overlap checking;
- PostGIS, APIs, UI, QR, plan extraction or LiDAR processing.

## Acceptance criteria

- The same normalized inputs always produce the same code.
- Encode/decode round trips stay within 0.25 m quantization error.
- A single-character payload change invalidates the checksum in the test suite.
- Invalid ranges and malformed codes are rejected clearly.
- Tests run with the Python standard library only.

## Next proposed phase

Phase 2 should build one synthetic parcel and one simple tower dataset, then add
an exact geometry registry. Before starting it, agree on:

1. whether the demo parent ULPIN will be explicitly synthetic;
2. relative building heights versus a named vertical datum;
3. PostGIS availability versus an in-memory geometry MVP;
4. whether the first UI uses MapLibre extrusion or CesiumJS.

