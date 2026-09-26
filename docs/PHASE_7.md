# Phase 7 — Signed offline credential

Date: 2026-09-26

## Outcome

The Unit 302 portable property envelope now carries an ES256 (ECDSA P-256 with
SHA-256) signature. The offline verifier checks that signature against a cached
public-key trust store, rejects unknown or locally revoked key IDs, and enforces
the credential expiry timestamp.

The `BHU3D2` wire format is:

```text
BHU3D2.<base64url canonical JSON>.<issuer key ID>.<base64url P1363 signature>
```

The Python decoder and browser verifier validate the same 64-byte `r || s`
signature representation. The original `BHU3D1` checksum decoder remains
available for backward compatibility, but newly generated citizen payloads use
only `BHU3D2`.

## Build and run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_demo.py
.venv/bin/python scripts/build_citizen_payload.py
python3 -m http.server 8000
```

Open <http://localhost:8000/apps/verify/>.

## Security boundary

The committed private key and cached public key are intentionally synthetic demo
fixtures. Anyone can use the private key, so its signature conveys no real-world
authority. A production design must keep signing keys in controlled HSM/KMS
infrastructure and obtain trusted public keys, revocation state, and current
registry status through an authenticated government trust service.
