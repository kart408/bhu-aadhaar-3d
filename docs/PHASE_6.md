# Phase 6 — Offline citizen verification

Date: 2026-09-26

## Outcome

Unit 302 receives a portable property envelope containing its proposed 3D ULPIN,
exact synthetic bounds, height band, area and volume. SHA-256 protects the
payload against accidental or casual modification. A QR SVG contains the same
envelope.

The browser verifies the checksum locally, displays the property card, supports
QR image scanning where the browser provides `BarcodeDetector`, and caches the
verification application for offline reuse. Pasting the envelope is the reliable
cross-browser fallback.

## Build and run

```bash
python3 scripts/build_demo.py
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_citizen_payload.py
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/verify/> once, then reload it in airplane mode.

## Security boundary

A checksum detects changed bytes but does not establish who issued the payload.
Production would require a government-controlled digital signature, certificate
validation, revocation/status checks and authoritative registry lookup. The UI
therefore says “checksum valid,” never “ownership verified.”
