"""SQLite-backed proposal workflow with server-side spatial validation."""

from __future__ import annotations

import json
import re
import sqlite3
import hashlib
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

PROPOSAL_ID = re.compile(r"^\d{14}-P3D-[0-9A-F]{12}$")


class ProposalValidationError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _intersects(a: list[float], b: list[float]) -> bool:
    return (max(a[0], b[0]) < min(a[2], b[2]) and
            max(a[1], b[1]) < min(a[3], b[3]) and
            max(a[4], b[4]) < min(a[5], b[5]))


def _validate_payload(payload: dict) -> dict:
    if payload.get("schema") != "BHU3D_PROPERTY_PROPOSAL_V1":
        raise ProposalValidationError("unsupported proposal schema")
    if not PROPOSAL_ID.fullmatch(str(payload.get("id", ""))):
        raise ProposalValidationError("invalid proposal identifier")
    if not re.fullmatch(r"\d{14}", str(payload.get("parent_ulpin", ""))):
        raise ProposalValidationError("invalid parent ULPIN")
    if not str(payload["id"]).startswith(f"{payload['parent_ulpin']}-"):
        raise ProposalValidationError("proposal identifier must match parent ULPIN")
    bounds = payload.get("bounds_m")
    if not (isinstance(bounds, list) and len(bounds) == 6 and
            all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in bounds) and
            bounds[0] < bounds[2] and bounds[1] < bounds[3] and bounds[4] < bounds[5]):
        raise ProposalValidationError("invalid 3D bounds")
    for field in ("applicant", "property_type", "unit", "address", "geometry_source"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            raise ProposalValidationError(f"{field} is required")
    return {key: payload[key] for key in (
        "schema", "id", "parent_ulpin", "applicant", "property_type", "unit",
        "address", "bounds_m", "geometry_source", "provenance",
    )}


class ProposalRegistry:
    def __init__(self, database: str | Path, geojson: str | Path):
        self.database = str(database)
        data = json.loads(Path(geojson).read_text())
        self.features = data["features"]
        self.registered = [feature for feature in self.features
                           if feature["properties"].get("registration_status") != "REJECTED"]
        self.parcel_bounds = [-20, -15, 20, 15, -10, 20]
        self._initialize()

    def parcel_model(self, parent_ulpin: str) -> dict | None:
        if not re.fullmatch(r"\d{14}", parent_ulpin):
            raise ProposalValidationError("ULPIN must contain exactly 14 digits")
        features = [feature for feature in self.features
                    if feature["properties"].get("ulpin3d", "").split("-")[0] == parent_ulpin]
        stored = self.registrations(parent_ulpin)
        for registration in stored:
            x1, y1, x2, y2, z1, z2 = registration["bounds_m"]
            area = (x2 - x1) * (y2 - y1)
            features.append({
                "type": "Feature", "id": registration["proposal_id"], "geometry": None,
                "properties": {
                    "key": registration["unit"], "kind": "unit",
                    "ulpin3d": registration["proposal_id"],
                    "base_m": z1, "top_m": z2, "height_m": z2 - z1,
                    "area_m2": area, "volume_m3": area * (z2 - z1),
                    "local_bounds_m": registration["bounds_m"],
                    "data_status": "SYNTHETIC_DEMO",
                    "registration_status": "REGISTERED_ADMINISTRATIVE",
                    "registration_basis": registration["registration_basis"],
                    "geometry_source": registration["geometry_source"],
                    "approved_at": registration["approved_at"],
                },
            })
        if not features:
            return None
        registered = [feature for feature in features
                      if feature["properties"].get("registration_status") != "REJECTED"]
        rejected = [feature for feature in features
                    if feature["properties"].get("registration_status") == "REJECTED"]
        return {
            "type": "FeatureCollection",
            "parent_ulpin": parent_ulpin,
            "data_status": "SYNTHETIC_DEMO",
            "features": features,
            "summary": {
                "registered_volumes": len(registered),
                "rejected_proposals": len(rejected),
                "registered_volume_m3": sum(item["properties"]["volume_m3"] for item in registered),
                "validation": "REGISTERED_VOLUMES_VALIDATED",
            },
        }

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    submitted_at TEXT NOT NULL,
                    decided_at TEXT,
                    decided_by TEXT
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    detail_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS registered_properties (
                    proposal_id TEXT PRIMARY KEY,
                    parent_ulpin TEXT NOT NULL,
                    registration_json TEXT NOT NULL,
                    approved_at TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    FOREIGN KEY (proposal_id) REFERENCES proposals(id)
                )
            """)
            missing = connection.execute("""
                SELECT p.* FROM proposals p
                LEFT JOIN registered_properties r ON r.proposal_id = p.id
                WHERE p.status = 'APPROVED' AND r.proposal_id IS NULL
            """).fetchall()
            for row in missing:
                payload = json.loads(row["payload_json"])
                validation = json.loads(row["validation_json"])
                registration = {
                    "proposal_id": row["id"], "parent_ulpin": payload["parent_ulpin"],
                    "property_type": payload["property_type"], "unit": payload["unit"],
                    "address": payload["address"], "bounds_m": payload["bounds_m"],
                    "geometry_source": payload["geometry_source"], "provenance": payload["provenance"],
                    "registration_basis": "ADMINISTRATIVE_GEOMETRY_WAIVER" if not validation["accepted"] else "SPATIAL_VALIDATION_PASSED",
                }
                connection.execute(
                    "INSERT INTO registered_properties VALUES (?, ?, ?, ?, ?)",
                    (row["id"], payload["parent_ulpin"], json.dumps(registration, separators=(",", ":")),
                     row["decided_at"] or row["submitted_at"], row["decided_by"] or "MIGRATION"),
                )
                self._append_event(connection, row["id"], "REGISTERED_PROPERTY_BACKFILLED", {
                    "parent_ulpin": payload["parent_ulpin"],
                    "registration_basis": registration["registration_basis"],
                })

    @staticmethod
    def _event_hash(previous_hash: str, proposal_id: str, event_type: str,
                    detail_json: str, occurred_at: str) -> str:
        material = "\x1f".join((previous_hash, proposal_id, event_type, detail_json, occurred_at))
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _append_event(self, connection: sqlite3.Connection, proposal_id: str,
                      event_type: str, detail: dict, occurred_at: str | None = None) -> None:
        previous = connection.execute(
            "SELECT event_hash FROM audit_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        previous_hash = previous["event_hash"] if previous else "0" * 64
        timestamp = occurred_at or _now()
        detail_json = json.dumps(detail, sort_keys=True, separators=(",", ":"))
        event_hash = self._event_hash(previous_hash, proposal_id, event_type, detail_json, timestamp)
        connection.execute(
            "INSERT INTO audit_events (proposal_id,event_type,detail_json,occurred_at,previous_hash,event_hash) VALUES (?,?,?,?,?,?)",
            (proposal_id, event_type, detail_json, timestamp, previous_hash, event_hash),
        )

    def spatial_validation(self, bounds: list[float], parent_ulpin: str) -> dict:
        parcel = self.parcel_bounds
        inside = (parcel[0] <= bounds[0] and bounds[2] <= parcel[2] and
                  parcel[1] <= bounds[1] and bounds[3] <= parcel[3])
        conflicts = [feature["properties"]["key"] for feature in self.registered
                     if feature["properties"].get("ulpin3d", "").split("-")[0] == parent_ulpin
                     and _intersects(bounds, feature["properties"]["local_bounds_m"])]
        errors = [] if inside else ["OUTSIDE_PARENT_PARCEL"]
        return {"accepted": not conflicts and not errors, "conflicts": conflicts, "errors": errors}

    def submit(self, payload: dict) -> dict:
        clean = _validate_payload(payload)
        validation = self.spatial_validation(clean["bounds_m"], clean["parent_ulpin"])
        timestamp = _now()
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO proposals VALUES (?, ?, ?, 'PENDING_REVIEW', ?, NULL, NULL)",
                (clean["id"], json.dumps(clean, separators=(",", ":")),
                 json.dumps(validation, separators=(",", ":")), timestamp),
            )
            if cursor.rowcount:
                self._append_event(connection, clean["id"], "PROPOSAL_SUBMITTED", {
                    "geometry_source": clean["geometry_source"], "parent_ulpin": clean["parent_ulpin"],
                }, timestamp)
                self._append_event(connection, clean["id"], "SPATIAL_VALIDATION_COMPLETED", validation, timestamp)
        return self.get(clean["id"])

    def get(self, proposal_id: str) -> dict | None:
        with closing(self._connect()) as connection, connection:
            row = connection.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,)).fetchone()
            stored = connection.execute(
                "SELECT 1 FROM registered_properties WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
        if row is None:
            return None
        return {
            "proposal": json.loads(row["payload_json"]),
            "validation": json.loads(row["validation_json"]),
            "status": row["status"], "submitted_at": row["submitted_at"],
            "decided_at": row["decided_at"], "decided_by": row["decided_by"],
            "registration_stored": stored is not None,
        }

    def decide(self, proposal_id: str, decision: str, officer: str, override_reason: str = "") -> dict:
        if decision not in {"APPROVED", "REJECTED"}:
            raise ProposalValidationError("decision must be APPROVED or REJECTED")
        record = self.get(proposal_id)
        if record is None:
            raise KeyError(proposal_id)
        if record["status"] != "PENDING_REVIEW":
            raise ProposalValidationError("proposal already decided")
        geometry_waived = decision == "APPROVED" and not record["validation"]["accepted"]
        if geometry_waived and not override_reason.strip():
            raise ProposalValidationError("a geometry waiver reason is required to approve without spatial validation")
        if not officer.strip():
            raise ProposalValidationError("officer identity is required")
        with closing(self._connect()) as connection, connection:
            timestamp = _now()
            connection.execute(
                "UPDATE proposals SET status = ?, decided_at = ?, decided_by = ? WHERE id = ?",
                (decision, timestamp, officer.strip(), proposal_id),
            )
            if decision == "APPROVED":
                payload = record["proposal"]
                registration = {
                    "proposal_id": proposal_id,
                    "parent_ulpin": payload["parent_ulpin"],
                    "property_type": payload["property_type"],
                    "unit": payload["unit"],
                    "address": payload["address"],
                    "bounds_m": payload["bounds_m"],
                    "geometry_source": payload["geometry_source"],
                    "provenance": payload["provenance"],
                    "registration_basis": "ADMINISTRATIVE_GEOMETRY_WAIVER" if geometry_waived else "SPATIAL_VALIDATION_PASSED",
                }
                connection.execute(
                    "INSERT INTO registered_properties VALUES (?, ?, ?, ?, ?)",
                    (proposal_id, payload["parent_ulpin"], json.dumps(registration, separators=(",", ":")),
                     timestamp, officer.strip()),
                )
            self._append_event(connection, proposal_id, "REGISTRAR_DECISION_RECORDED", {
                "decision": decision, "officer": officer.strip(),
                "geometry_check": "WAIVED" if geometry_waived else "PASSED",
                "override_reason": override_reason.strip() if geometry_waived else None,
            }, timestamp)
            if decision == "APPROVED":
                self._append_event(connection, proposal_id, "REGISTERED_PROPERTY_STORED", {
                    "parent_ulpin": record["proposal"]["parent_ulpin"],
                    "registration_basis": registration["registration_basis"],
                }, timestamp)
        return self.get(proposal_id)

    def registrations(self, parent_ulpin: str | None = None) -> list[dict]:
        query = "SELECT * FROM registered_properties"
        parameters: tuple[str, ...] = ()
        if parent_ulpin is not None:
            query += " WHERE parent_ulpin = ?"
            parameters = (parent_ulpin,)
        query += " ORDER BY approved_at, proposal_id"
        with closing(self._connect()) as connection, connection:
            rows = connection.execute(query, parameters).fetchall()
        return [{
            **json.loads(row["registration_json"]),
            "approved_at": row["approved_at"], "approved_by": row["approved_by"],
        } for row in rows]

    def verify_audit_chain(self) -> bool:
        with closing(self._connect()) as connection, connection:
            rows = connection.execute("SELECT * FROM audit_events ORDER BY sequence").fetchall()
        previous_hash = "0" * 64
        for row in rows:
            expected = self._event_hash(previous_hash, row["proposal_id"], row["event_type"],
                                        row["detail_json"], row["occurred_at"])
            if row["previous_hash"] != previous_hash or row["event_hash"] != expected:
                return False
            previous_hash = row["event_hash"]
        return True

    def audit(self, proposal_id: str) -> dict:
        with closing(self._connect()) as connection, connection:
            rows = connection.execute(
                "SELECT * FROM audit_events WHERE proposal_id = ? ORDER BY sequence", (proposal_id,)
            ).fetchall()
        return {
            "proposal_id": proposal_id,
            "chain_valid": self.verify_audit_chain(),
            "events": [{
                "sequence": row["sequence"], "type": row["event_type"],
                "detail": json.loads(row["detail_json"]), "occurred_at": row["occurred_at"],
                "previous_hash": row["previous_hash"], "event_hash": row["event_hash"],
            } for row in rows],
        }
