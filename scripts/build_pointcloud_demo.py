#!/usr/bin/env python3
"""Build a deterministic, unit-scoped synthetic point cloud for Shop G-12."""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "generated" / "abc_complex_g12_pointcloud.json"


def build() -> dict:
    random.seed(302)
    x1, y1, x2, y2, z1, z2 = -9.048, -5.524, -2.952, -2.476, 0.0, 3.6576
    points: list[list[float]] = []
    # Dense floor and ceiling returns drive Z-cluster detection.
    for z in (z1, z2):
        for ix in range(9):
            for iy in range(6):
                x = x1 + (x2 - x1) * ix / 8
                y = y1 + (y2 - y1) * iy / 5
                points.append([round(x, 4), round(y, 4), round(z + random.uniform(-0.018, 0.018), 4)])
    # Sparse wall returns preserve the horizontal extents without becoming Z surfaces.
    for iz in range(1, 8):
        z = z1 + (z2 - z1) * iz / 8
        points.extend([[x1, y1, round(z, 4)], [x2, y1, round(z, 4)], [x2, y2, round(z, 4)], [x1, y2, round(z, 4)]])
    return {
        "schema": "BHU3D_POINT_CLOUD_DEMO_V1",
        "data_status": "SYNTHETIC_DEMO",
        "property_key": "G-12",
        "coordinate_reference": "LOCAL_METRES_RELATIVE_TO_BUILDING_ANCHOR",
        "vertical_reference": "RELATIVE_TO_SYNTHETIC_GROUND_LEVEL",
        "acquired_at": "2026-09-26T00:00:00Z",
        "accuracy_m": 0.03,
        "points": points,
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n")
    print(f"Built {OUTPUT.name} with {len(build()['points'])} synthetic points")
