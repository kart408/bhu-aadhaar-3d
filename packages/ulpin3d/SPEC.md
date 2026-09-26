# Proposed 3D ULPIN extension — prototype specification v0.1

Status: experimental; not an official DoLR standard.

## Display format

```text
PPPPPPPPPPPPPP-HHHH-ZZZZ-C
```

- `P` (14 digits): existing parent ULPIN, preserved unchanged.
- `H` (4 Crockford Base32 characters): relative horizontal centroid.
- `Z` (4 Crockford Base32 characters): lower height and volume height.
- `C` (1 Crockford Base32 character): generalized Luhn mod-32 check.

The canonical stored representation omits hyphens and contains 23 characters.

## Horizontal field

1. Work in a metric projected CRS selected for the source data.
2. Subtract parcel centroid easting/northing from unit centroid.
3. Quantize each offset to the nearest 0.5 m.
4. Store each as signed 10-bit two's-complement.
5. Interleave easting and northing bits, most-significant bit first.
6. Encode the resulting 20 bits as four Crockford Base32 characters.

Representable offset range: -256.0 m to +255.5 m on each axis.

## Vertical field

1. Quantize lower height to 0.5 m and store as signed 10-bit two's-complement.
2. Quantize `(ceiling - floor)` to 0.5 m and store as unsigned 10-bit.
3. Concatenate the two 10-bit values and encode as four Base32 characters.

Lower-height range: -256.0 m to +255.5 m. Unit-height range: 0.5 m to
511.5 m. Height datum/reference is metadata in the registry and is mandatory.

## Important semantics

The code is a deterministic compact locator, not the legal boundary itself.
Exact footprint, CRS, height datum, provenance and rights live in the registry.
Exact overlap detection uses registered volume geometry. A decoded code can only
provide a coarse screening check when footprint dimensions are supplied.

## Versioning decision

Version is registry metadata in v0.1, not encoded in the string. Before any
non-demo deployment, the standard must add an explicit version mechanism.

