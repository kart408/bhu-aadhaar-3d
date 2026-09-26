#!/usr/bin/env python3
"""Generate the synthetic Phase 5 reconciliation report."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.reconciliation import reconcile

RECORDS = ROOT / "data" / "seed" / "property_records.json"
GEOMETRY = ROOT / "data" / "generated" / "demo_volumes.geojson"
OUTPUT = ROOT / "data" / "generated" / "reconciliation_report.json"


def build_report(records: dict, geojson: dict) -> dict:
    registered_features = [
        feature for feature in geojson["features"]
        if feature["properties"].get("registration_status") != "REJECTED"
    ]
    area_by_key = {
        feature["properties"]["key"]: feature["properties"]["area_m2"]
        for feature in registered_features
    }
    report = reconcile(
        records["units"],
        records["rights"],
        area_by_key,
        area_tolerance_pct=records["metadata"]["area_tolerance_pct"],
    )
    report["dataset_status"] = records["metadata"]["status"]
    report["parent_ulpin"] = records["metadata"]["parent_ulpin"]
    return report


def main() -> None:
    if not GEOMETRY.exists():
        raise SystemExit("Run `python3 scripts/build_demo.py` first.")
    records = json.loads(RECORDS.read_text())
    geojson = json.loads(GEOMETRY.read_text())
    report = build_report(records, geojson)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Reconciliation status: {report['status']}")
    print(f"Findings: {report['finding_count']}")
    for finding in report["findings"]:
        print(f"{finding['severity']}: {finding['rule']} · {finding['subject']}")


if __name__ == "__main__":
    main()

