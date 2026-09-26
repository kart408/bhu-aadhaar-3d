"""Checksum-protected, explicitly non-official property payload format."""

from __future__ import annotations

import base64
import hashlib
import json

PREFIX = "BHU3D1"
SIGNED_PREFIX = "BHU3D2"


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def create_envelope(payload: dict) -> str:
    raw = _canonical(payload)
    encoded = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    checksum = hashlib.sha256(raw).hexdigest()[:16]
    return f"{PREFIX}.{encoded}.{checksum}"


def decode_envelope(envelope: str) -> dict:
    try:
        prefix, encoded, checksum = envelope.strip().split(".")
    except ValueError as error:
        raise ValueError("payload must contain prefix, data and checksum") from error
    if prefix != PREFIX:
        raise ValueError("unsupported property payload version")
    padding = "=" * (-len(encoded) % 4)
    try:
        raw = base64.urlsafe_b64decode(encoded + padding)
    except Exception as error:
        raise ValueError("invalid property payload encoding") from error
    expected = hashlib.sha256(raw).hexdigest()[:16]
    if checksum.lower() != expected:
        raise ValueError("property payload checksum mismatch")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("property payload is not valid JSON") from error
    if payload.get("data_status") != "SYNTHETIC_DEMO":
        raise ValueError("prototype verifier accepts synthetic demo payloads only")
    return payload


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def create_signed_envelope(payload: dict, private_key_pem: bytes, key_id: str) -> str:
    """Create a browser-verifiable P-256 envelope.

    The signature is IEEE P1363 (r || s), matching the Web Crypto API.
    """
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

    raw = _canonical(payload)
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(private_key.curve, ec.SECP256R1):
        raise ValueError("issuer key must be a P-256 private key")
    der_signature = private_key.sign(raw, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_signature)
    signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return f"{SIGNED_PREFIX}.{_base64url(raw)}.{key_id}.{_base64url(signature)}"


def public_jwk(private_key_pem: bytes, key_id: str) -> dict:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey) or not isinstance(private_key.curve, ec.SECP256R1):
        raise ValueError("issuer key must be a P-256 private key")
    numbers = private_key.public_key().public_numbers()
    return {
        "kty": "EC", "crv": "P-256", "alg": "ES256", "use": "sig", "kid": key_id,
        "x": _base64url(numbers.x.to_bytes(32, "big")),
        "y": _base64url(numbers.y.to_bytes(32, "big")),
    }


def decode_signed_envelope(envelope: str, public_key_jwk: dict) -> dict:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature

    try:
        prefix, encoded, key_id, encoded_signature = envelope.strip().split(".")
    except ValueError as error:
        raise ValueError("signed payload must contain prefix, data, key id and signature") from error
    if prefix != SIGNED_PREFIX:
        raise ValueError("unsupported signed property payload version")
    if key_id != public_key_jwk.get("kid"):
        raise ValueError("unknown issuer key")
    try:
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        signature = base64.urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
    except Exception as error:
        raise ValueError("invalid signed payload encoding") from error
    if len(signature) != 64:
        raise ValueError("invalid P-256 signature length")
    r, s = int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big")
    public_numbers = ec.EllipticCurvePublicNumbers(
        int.from_bytes(base64.urlsafe_b64decode(public_key_jwk["x"] + "=" * (-len(public_key_jwk["x"]) % 4)), "big"),
        int.from_bytes(base64.urlsafe_b64decode(public_key_jwk["y"] + "=" * (-len(public_key_jwk["y"]) % 4)), "big"),
        ec.SECP256R1(),
    )
    try:
        public_numbers.public_key().verify(encode_dss_signature(r, s), raw, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        raise ValueError("property payload signature mismatch") from error
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("property payload is not valid JSON") from error
    if _canonical(payload) != raw:
        raise ValueError("property payload is not canonical")
    if payload.get("data_status") != "SYNTHETIC_DEMO":
        raise ValueError("prototype verifier accepts synthetic demo payloads only")
    return payload
