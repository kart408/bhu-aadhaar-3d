"""Transparent, deterministic reconciliation rules.

These checks flag inconsistent submitted records. They do not decide ownership.
"""

from __future__ import annotations

from collections import Counter


def reconcile(
    units: list[dict],
    rights: list[dict],
    geometry_area_by_key: dict[str, float],
    area_tolerance_pct: float = 5.0,
    share_tolerance_pct: float = 0.01,
) -> dict:
    findings: list[dict] = []

    share_total = round(sum(float(unit["share_pct"]) for unit in units), 4)
    if abs(share_total - 100.0) > share_tolerance_pct:
        findings.append(
            {
                "rule": "SHARE_TOTAL",
                "severity": "HIGH",
                "subject": "PARCEL",
                "message": f"Undivided shares total {share_total:.2f}%, expected 100.00%.",
                "measured": share_total,
                "expected": 100.0,
            }
        )

    for unit in units:
        key = unit["volume_key"]
        mapped = geometry_area_by_key.get(key)
        if mapped is None:
            findings.append(
                {
                    "rule": "MISSING_GEOMETRY",
                    "severity": "HIGH",
                    "subject": key,
                    "message": "No registered geometry is available for this unit record.",
                }
            )
            continue
        declared = float(unit["declared_carpet_m2"])
        difference_pct = abs(declared - mapped) / mapped * 100
        if difference_pct > area_tolerance_pct:
            findings.append(
                {
                    "rule": "AREA_MISMATCH",
                    "severity": "MEDIUM",
                    "subject": key,
                    "message": f"Declared area differs from mapped area by {difference_pct:.1f}%.",
                    "declared_m2": declared,
                    "mapped_m2": mapped,
                    "difference_pct": round(difference_pct, 2),
                }
            )

    active_ownership = Counter(
        right["volume_key"]
        for right in rights
        if right["type"] == "ownership" and right.get("active", True)
    )
    for key, count in sorted(active_ownership.items()):
        if count > 1:
            deed_refs = [
                right["deed_ref"] for right in rights
                if right["volume_key"] == key
                and right["type"] == "ownership"
                and right.get("active", True)
            ]
            findings.append(
                {
                    "rule": "DUPLICATE_ACTIVE_RIGHT",
                    "severity": "CRITICAL",
                    "subject": key,
                    "message": f"{count} active exclusive ownership claims reference the same volume.",
                    "deed_refs": deed_refs,
                }
            )

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda item: (severity_order[item["severity"]], item["rule"], item["subject"]))
    counts = Counter(item["severity"] for item in findings)
    return {
        "status": "FLAGGED" if findings else "CLEAR",
        "rules_run": 3,
        "unit_records_checked": len(units),
        "rights_checked": len(rights),
        "share_total_pct": share_total,
        "area_tolerance_pct": area_tolerance_pct,
        "finding_count": len(findings),
        "severity_counts": {
            "critical": counts["CRITICAL"],
            "high": counts["HIGH"],
            "medium": counts["MEDIUM"],
            "low": counts["LOW"],
        },
        "findings": findings,
        "disclaimer": "Automated consistency flags only; findings require authorized human review.",
    }

