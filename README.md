# Bhu-Aadhaar 3D Prototype

Minimal SIH prototype for deriving and validating proposed 3D property identifiers
under an existing land-parcel ULPIN.

> This is a hackathon prototype and **not an official DoLR identifier standard**.
> The existing 14-digit parent ULPIN is preserved unchanged.

## Current status

Phases 1 through 16 are complete:

- official-source assumptions documented;
- prototype identifier format specified;
- dependency-free Python reference implementation added;
- round-trip, checksum, range and overlap tests added.
- synthetic tower, basement and underground utility dataset added;
- exact rectangular-volume validation and GeoJSON generation added.
- interactive dependency-free 3D demo viewer added.
- registrar parcel-selection, validation, approval and rejection simulation added.
- share, area and duplicate-right reconciliation engine and dashboard added.
- checksum-protected QR payload and offline citizen verification PWA added.
- ES256 issuer signatures, cached trust keys, expiry and revocation checks added.
- ordinary property intake now generates a metric 3D box from building, unit, floor and dimensions.
- synthetic point-cloud analysis now detects floor/ceiling Z surfaces and generates the same proposal geometry.
- citizen-generated proposals now transfer into registrar boundary and overlap validation.
- a SQLite registry API now persists submissions and enforces validation before registrar decisions.
- SHA-256-chained durable audit events now expose workflow history and detect stored-event tampering.
- ULPIN lookup now isolates one building model with 3D volume, LiDAR overlay and registration findings.
- registrar review is simplified to essential submitted details and an explicitly audited administrative approval waiver.
- approved properties are durably stored and automatically merged into their ULPIN's public 3D model.
- intake now accepts arbitrary property labels, addresses, units and numeric floors with deterministic offline demo placement.

Read these documents before building another component:

1. [`docs/PHASE_1.md`](docs/PHASE_1.md)
2. [`packages/ulpin3d/SPEC.md`](packages/ulpin3d/SPEC.md)
3. [`docs/PHASE_2.md`](docs/PHASE_2.md)
4. [`docs/PHASE_3.md`](docs/PHASE_3.md)
5. [`docs/PHASE_4.md`](docs/PHASE_4.md)
6. [`docs/PHASE_5.md`](docs/PHASE_5.md)
7. [`docs/PHASE_6.md`](docs/PHASE_6.md)
8. [`docs/PHASE_7.md`](docs/PHASE_7.md)
9. [`docs/PHASE_8.md`](docs/PHASE_8.md)
10. [`docs/PHASE_9.md`](docs/PHASE_9.md)
11. [`docs/PHASE_10.md`](docs/PHASE_10.md)
12. [`docs/PHASE_11.md`](docs/PHASE_11.md)
13. [`docs/PHASE_12.md`](docs/PHASE_12.md)
14. [`docs/PHASE_13.md`](docs/PHASE_13.md)
15. [`docs/PHASE_14.md`](docs/PHASE_14.md)
16. [`docs/PHASE_15.md`](docs/PHASE_15.md)
17. [`docs/PHASE_16.md`](docs/PHASE_16.md)

## Run the Phase 1 tests

```bash
python3 -m unittest discover -s tests -v
```

Build the Phase 2 demo data:

```bash
python3 scripts/build_demo.py
python3 scripts/reconcile_demo.py
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_citizen_payload.py
```

Run the Phase 3 viewer:

```bash
.venv/bin/python scripts/run_registry_server.py
```

Then open <http://127.0.0.1:8000/apps/viewer/>. Use `python3 -m http.server 8000`
only when you intentionally want the browser-storage fallback without the API.

Registrar simulation: <http://localhost:8000/apps/registrar/>.

Reconciliation dashboard: <http://localhost:8000/apps/reconcile/>.

Citizen verification: <http://localhost:8000/apps/verify/>.

Property intake and automatic 3D generation: <http://localhost:8000/apps/intake/>.

## Tiny example

```python
from packages.ulpin3d import encode, decode, validate

code = encode(
    parcel_ulpin="12345678901234",
    centroid_e=500010.0,
    centroid_n=1450005.0,
    parcel_centroid_e=500000.0,
    parcel_centroid_n=1450000.0,
    floor_h=12.0,
    ceil_h=15.0,
)

assert validate(code)
print(code)
print(decode(code))
```
