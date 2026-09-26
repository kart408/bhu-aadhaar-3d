#!/usr/bin/env python3
"""Build Phase 2 GeoJSON and a validation report from the synthetic seed."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.geometry import RectVolume, find_conflicts, validate_volume
from packages.ulpin3d import encode

SEED_PATH = ROOT / "data" / "seed" / "demo_tower.json"
OUTPUT_DIR = ROOT / "data" / "generated"


def as_volume(raw: dict) -> RectVolume:
    return RectVolume(raw["key"], raw["kind"], *raw["bounds"])


def build(seed: dict) -> tuple[dict, dict]:
    metadata = seed["metadata"]
    parcel = as_volume(seed["parcel"])
    registered = [as_volume(item) for item in seed["volumes"]]
    proposed = [as_volume(item) for item in seed["proposed_conflicts"]]
    parcel_centre = parcel.centroid

    features = []
    code_by_key = {}
    for volume in registered:
        x, y, _ = volume.centroid
        code = encode(
            metadata["parent_ulpin"],
            x,
            y,
            parcel_centre[0],
            parcel_centre[1],
            volume.z_min,
            volume.z_max,
        )
        code_by_key[volume.key] = code
        features.append(volume.to_feature(code, tuple(metadata["map_anchor_wgs84"])))

    registered_conflicts = find_conflicts(registered)
    proposals = []
    for candidate in proposed:
        conflicts = [item.key for item in registered if candidate.intersects(item)]
        errors = validate_volume(candidate, parcel)
        accepted = not conflicts and not errors
        proposal_result = {
            "key": candidate.key,
            "accepted": accepted,
            "conflicts_with": conflicts,
            "validation_errors": errors,
        }
        proposals.append(proposal_result)
        x, y, _ = candidate.centroid
        code = encode(
            metadata["parent_ulpin"], x, y, parcel_centre[0], parcel_centre[1],
            candidate.z_min, candidate.z_max
        )
        feature = candidate.to_feature(code, tuple(metadata["map_anchor_wgs84"]))
        feature["properties"].update(
            {
                "registration_status": "ACCEPTED" if accepted else "REJECTED",
                "conflicts_with": conflicts,
                "validation_errors": errors,
            }
        )
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "name": "Bhu-Aadhaar 3D synthetic demo",
        "metadata": metadata,
        "features": features,
    }
    report = {
        "dataset_status": metadata["status"],
        "registered_volume_count": len(registered),
        "registered_conflicts": registered_conflicts,
        "all_registered_volumes_valid": not registered_conflicts
        and all(not validate_volume(item, parcel) for item in registered),
        "proposed_insert_results": proposals,
        "identifiers": code_by_key,
    }
    return geojson, report


def main() -> None:
    seed = json.loads(SEED_PATH.read_text())
    geojson, report = build(seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "demo_volumes.geojson").write_text(json.dumps(geojson, indent=2) + "\n")
    (OUTPUT_DIR / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Built {report['registered_volume_count']} valid registered volumes")
    print(f"Registered conflicts: {len(report['registered_conflicts'])}")
    for result in report["proposed_insert_results"]:
        print(f"{result['key']}: {'ACCEPT' if result['accepted'] else 'REJECT'}")


if __name__ == "__main__":
    main()
