#!/usr/bin/env python3
"""Build Unit 302's offline verification payload and optional QR SVG."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.verification import create_signed_envelope, decode_signed_envelope, public_jwk

GEOJSON = ROOT / "data" / "generated" / "demo_volumes.geojson"
OUTPUT = ROOT / "data" / "generated" / "citizen_payload.json"
QR_OUTPUT = ROOT / "apps" / "verify" / "unit-302-qr.svg"
KEY_FILE = ROOT / "data" / "seed" / "demo_issuer_private_key.pem"
TRUST_STORE = ROOT / "apps" / "verify" / "trusted-issuers.json"
KEY_ID = "demo-dolr-lab-p256-2026"


def build(feature: dict) -> dict:
    properties = feature["properties"]
    payload = {
        "version": 1,
        "data_status": "SYNTHETIC_DEMO",
        "property_key": properties["key"],
        "parent_ulpin": properties["ulpin3d"].split("-")[0],
        "ulpin3d": properties["ulpin3d"],
        "kind": properties["kind"],
        "bounds_m": properties["local_bounds_m"],
        "base_m": properties["base_m"],
        "top_m": properties["top_m"],
        "area_m2": properties["area_m2"],
        "volume_m3": properties["volume_m3"],
        "horizontal_reference": "LOCAL_METRES_FOR_DEMO_ONLY",
        "vertical_reference": "RELATIVE_TO_SYNTHETIC_GROUND_LEVEL",
        "issuer": "BHU3D PROTOTYPE LAB — NOT A GOVERNMENT ISSUER",
        "issued_at": "2026-09-26T00:00:00Z",
        "expires_at": "2027-09-26T00:00:00Z",
    }
    private_key = KEY_FILE.read_bytes()
    issuer_key = public_jwk(private_key, KEY_ID)
    envelope = create_signed_envelope(payload, private_key, KEY_ID)
    assert decode_signed_envelope(envelope, issuer_key) == payload
    return {"envelope": envelope, "payload": payload, "key_id": KEY_ID, "algorithm": "ES256"}


def write_qr(envelope: str) -> bool:
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        print("QR dependency unavailable; JSON payload built without SVG.")
        print("Install with: python3 -m pip install -r requirements.txt")
        return False
    factory = qrcode.image.svg.SvgPathImage
    image = qrcode.make(envelope, image_factory=factory, box_size=8, border=3)
    image.save(QR_OUTPUT)
    return True


def main() -> None:
    if not GEOJSON.exists():
        raise SystemExit("Run `python3 scripts/build_demo.py` first.")
    geojson = json.loads(GEOJSON.read_text())
    feature = next(item for item in geojson["features"] if item["properties"]["key"] == "UNIT-302")
    document = build(feature)
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    TRUST_STORE.write_text(json.dumps({
        "version": 1,
        "purpose": "SYNTHETIC DEMO TRUST STORE ONLY",
        "issuers": [public_jwk(KEY_FILE.read_bytes(), KEY_ID)],
        "revoked_key_ids": [],
    }, indent=2) + "\n")
    qr_written = write_qr(document["envelope"])
    print(f"Citizen payload built for {document['payload']['property_key']}")
    print(f"ES256-signed envelope length: {len(document['envelope'])}")
    print(f"QR SVG: {'built' if qr_written else 'not built'}")


if __name__ == "__main__":
    main()
