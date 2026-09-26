import unittest
from pathlib import Path

from packages.verification import (
    create_envelope, create_signed_envelope, decode_envelope,
    decode_signed_envelope, public_jwk,
)

ROOT = Path(__file__).resolve().parents[1]


class VerificationPayloadTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "version": 1,
            "data_status": "SYNTHETIC_DEMO",
            "property_key": "UNIT-302",
            "bounds_m": [0, -8, 12, 8, 6, 9],
        }

    def test_round_trip(self):
        self.assertEqual(decode_envelope(create_envelope(self.payload)), self.payload)

    def test_payload_is_deterministic(self):
        reversed_order = dict(reversed(list(self.payload.items())))
        self.assertEqual(create_envelope(self.payload), create_envelope(reversed_order))

    def test_tampering_is_detected(self):
        envelope = create_envelope(self.payload)
        prefix, encoded, checksum = envelope.split(".")
        replacement = "A" if encoded[-1] != "A" else "B"
        with self.assertRaises(ValueError):
            decode_envelope(f"{prefix}.{encoded[:-1]}{replacement}.{checksum}")

    def test_non_demo_payload_is_refused(self):
        payload = {**self.payload, "data_status": "OFFICIAL"}
        with self.assertRaises(ValueError):
            decode_envelope(create_envelope(payload))

    def test_signed_round_trip_and_tamper_detection(self):
        key = (ROOT / "data" / "seed" / "demo_issuer_private_key.pem").read_bytes()
        jwk = public_jwk(key, "test-demo-key")
        envelope = create_signed_envelope(self.payload, key, "test-demo-key")
        self.assertEqual(decode_signed_envelope(envelope, jwk), self.payload)
        prefix, encoded, kid, signature = envelope.split(".")
        replacement = "A" if encoded[-1] != "A" else "B"
        tampered = ".".join((prefix, encoded[:-1] + replacement, kid, signature))
        with self.assertRaisesRegex(ValueError, "signature mismatch"):
            decode_signed_envelope(tampered, jwk)

    def test_signed_envelope_rejects_unknown_key(self):
        key = (ROOT / "data" / "seed" / "demo_issuer_private_key.pem").read_bytes()
        envelope = create_signed_envelope(self.payload, key, "issuer-a")
        with self.assertRaisesRegex(ValueError, "unknown issuer key"):
            decode_signed_envelope(envelope, public_jwk(key, "issuer-b"))


if __name__ == "__main__":
    unittest.main()
