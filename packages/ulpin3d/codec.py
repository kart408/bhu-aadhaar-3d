"""Dependency-free reference codec for the proposed ULPIN 3D extension."""

from __future__ import annotations

from dataclasses import dataclass
import re

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
VALUE = {character: index for index, character in enumerate(ALPHABET)}
RESOLUTION_M = 0.5
CANONICAL_RE = re.compile(r"^[0-9]{14}[0-9A-HJKMNP-TV-Z]{9}$")


@dataclass(frozen=True)
class DecodedULPIN3D:
    parcel_ulpin: str
    de: float
    dn: float
    floor_h: float
    ceil_h: float


def _quantize(value: float) -> int:
    """Round half away from zero to avoid Python's banker rounding surprises."""
    scaled = value / RESOLUTION_M
    return int(scaled + 0.5) if scaled >= 0 else int(scaled - 0.5)


def _signed_to_bits(value: int, width: int = 10) -> int:
    minimum, maximum = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if not minimum <= value <= maximum:
        raise ValueError(f"signed value {value} is outside [{minimum}, {maximum}]")
    return value & ((1 << width) - 1)


def _bits_to_signed(value: int, width: int = 10) -> int:
    sign = 1 << (width - 1)
    return value - (1 << width) if value & sign else value


def _base32_encode(value: int, length: int) -> str:
    if not 0 <= value < 32**length:
        raise ValueError("value does not fit requested Base32 length")
    output = ["0"] * length
    for index in range(length - 1, -1, -1):
        output[index] = ALPHABET[value & 31]
        value >>= 5
    return "".join(output)


def _base32_decode(text: str) -> int:
    result = 0
    for character in text:
        try:
            result = result * 32 + VALUE[character]
        except KeyError as error:
            raise ValueError(f"invalid Crockford Base32 character: {character}") from error
    return result


def _interleave(east: int, north: int) -> int:
    result = 0
    for bit in range(9, -1, -1):
        result = (result << 1) | ((east >> bit) & 1)
        result = (result << 1) | ((north >> bit) & 1)
    return result


def _deinterleave(value: int) -> tuple[int, int]:
    east = north = 0
    for bit in range(9, -1, -1):
        east |= ((value >> (bit * 2 + 1)) & 1) << bit
        north |= ((value >> (bit * 2)) & 1) << bit
    return east, north


def _check_character(payload: str) -> str:
    factor, total = 2, 0
    for character in reversed(payload):
        codepoint = VALUE[character]
        addend = factor * codepoint
        factor = 1 if factor == 2 else 2
        total += (addend // 32) + (addend % 32)
    return ALPHABET[(32 - (total % 32)) % 32]


def _canonical(code: str) -> str:
    return code.replace("-", "").strip().upper()


def encode(
    parcel_ulpin: str,
    centroid_e: float,
    centroid_n: float,
    parcel_centroid_e: float,
    parcel_centroid_n: float,
    floor_h: float,
    ceil_h: float,
) -> str:
    """Encode relative centroid and vertical band under an existing parent ULPIN."""
    if not re.fullmatch(r"[0-9]{14}", parcel_ulpin):
        raise ValueError("prototype parent ULPIN must contain exactly 14 digits")
    if ceil_h <= floor_h:
        raise ValueError("ceiling height must be greater than floor height")

    east = _signed_to_bits(_quantize(centroid_e - parcel_centroid_e))
    north = _signed_to_bits(_quantize(centroid_n - parcel_centroid_n))
    horizontal = _base32_encode(_interleave(east, north), 4)

    floor = _signed_to_bits(_quantize(floor_h))
    height = _quantize(ceil_h - floor_h)
    if not 1 <= height <= 1023:
        raise ValueError("quantized unit height must be between 0.5 m and 511.5 m")
    vertical = _base32_encode((floor << 10) | height, 4)

    payload = f"{parcel_ulpin}{horizontal}{vertical}"
    check = _check_character(payload)
    return f"{parcel_ulpin}-{horizontal}-{vertical}-{check}"


def validate(code: str) -> bool:
    canonical = _canonical(code)
    if not CANONICAL_RE.fullmatch(canonical):
        return False
    return canonical[-1] == _check_character(canonical[:-1])


def decode(code: str) -> DecodedULPIN3D:
    canonical = _canonical(code)
    if not validate(canonical):
        raise ValueError("malformed ULPIN 3D code or checksum mismatch")

    east_bits, north_bits = _deinterleave(_base32_decode(canonical[14:18]))
    vertical = _base32_decode(canonical[18:22])
    floor_units = _bits_to_signed(vertical >> 10)
    height_units = vertical & 1023
    floor_h = floor_units * RESOLUTION_M
    return DecodedULPIN3D(
        parcel_ulpin=canonical[:14],
        de=_bits_to_signed(east_bits) * RESOLUTION_M,
        dn=_bits_to_signed(north_bits) * RESOLUTION_M,
        floor_h=floor_h,
        ceil_h=floor_h + height_units * RESOLUTION_M,
    )


def overlaps(
    code_a: str,
    code_b: str,
    footprint_a: tuple[float, float],
    footprint_b: tuple[float, float],
) -> bool:
    """Conservative axis-aligned screening only; not a legal geometry check."""
    a, b = decode(code_a), decode(code_b)
    if a.parcel_ulpin != b.parcel_ulpin:
        return False
    horizontal = (
        abs(a.de - b.de) < (footprint_a[0] + footprint_b[0]) / 2
        and abs(a.dn - b.dn) < (footprint_a[1] + footprint_b[1]) / 2
    )
    vertical = max(a.floor_h, b.floor_h) < min(a.ceil_h, b.ceil_h)
    return horizontal and vertical

