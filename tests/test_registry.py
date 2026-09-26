import tempfile
import unittest
import sqlite3
from contextlib import closing
from pathlib import Path

from packages.registry import ProposalRegistry, ProposalValidationError

ROOT = Path(__file__).resolve().parents[1]


def proposal(identifier="12345678901234-P3D-ABCDEF123456", bounds=None):
    return {
        "schema": "BHU3D_PROPERTY_PROPOSAL_V1",
        "id": identifier,
        "parent_ulpin": "12345678901234",
        "applicant": "Karthik Reddy",
        "property_type": "Shop",
        "unit": "G-12",
        "address": "ABC Complex, Hyderabad",
        "bounds_m": bounds or [-9.048, -5.524, -2.952, -2.476, 0, 3.6576],
        "geometry_source": "OWNER_SUPPLIED_DIMENSIONS",
        "provenance": {"dimension_unit": "feet"},
    }


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = ProposalRegistry(
            Path(self.temp.name) / "registry.sqlite3",
            ROOT / "data" / "generated" / "demo_volumes.geojson",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_submission_is_persisted_and_conflict_explained(self):
        record = self.registry.submit(proposal())
        self.assertEqual(record["status"], "PENDING_REVIEW")
        self.assertFalse(record["validation"]["accepted"])
        self.assertIn("UNIT-101", record["validation"]["conflicts"])
        self.assertEqual(self.registry.get(proposal()["id"]), record)
        audit = self.registry.audit(proposal()["id"])
        self.assertTrue(audit["chain_valid"])
        self.assertEqual([event["type"] for event in audit["events"]], [
            "PROPOSAL_SUBMITTED", "SPATIAL_VALIDATION_COMPLETED",
        ])

    def test_conflicted_proposal_cannot_be_approved(self):
        self.registry.submit(proposal())
        with self.assertRaisesRegex(ProposalValidationError, "waiver reason"):
            self.registry.decide(proposal()["id"], "APPROVED", "DEMO-OFFICER")
        decided = self.registry.decide(proposal()["id"], "REJECTED", "DEMO-OFFICER")
        self.assertEqual(decided["status"], "REJECTED")

    def test_conflicted_proposal_can_be_approved_with_audited_waiver(self):
        self.registry.submit(proposal())
        decided = self.registry.decide(
            proposal()["id"], "APPROVED", "DEMO-OFFICER",
            "Administrative registration requested; dimensional matching not applied.",
        )
        self.assertEqual(decided["status"], "APPROVED")
        self.assertTrue(decided["registration_stored"])
        stored = self.registry.registrations("12345678901234")
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["unit"], "G-12")
        self.assertEqual(stored[0]["registration_basis"], "ADMINISTRATIVE_GEOMETRY_WAIVER")
        event = next(item for item in self.registry.audit(proposal()["id"])["events"] if item["type"] == "REGISTRAR_DECISION_RECORDED")
        self.assertEqual(event["detail"]["geometry_check"], "WAIVED")
        self.assertEqual(self.registry.audit(proposal()["id"])["events"][-1]["type"], "REGISTERED_PROPERTY_STORED")

    def test_clean_proposal_can_be_approved_once(self):
        clean = proposal("12345678901234-P3D-ABCDEF123457", [-12, -8, 0, 8, 12, 15])
        self.registry.submit(clean)
        decided = self.registry.decide(clean["id"], "APPROVED", "DEMO-OFFICER")
        self.assertEqual(decided["status"], "APPROVED")
        with self.assertRaisesRegex(ProposalValidationError, "already decided"):
            self.registry.decide(clean["id"], "REJECTED", "DEMO-OFFICER")

    def test_invalid_schema_is_rejected(self):
        with self.assertRaises(ProposalValidationError):
            self.registry.submit({**proposal(), "bounds_m": [0, 0, 0]})

    def test_parcel_model_is_isolated_by_parent_ulpin(self):
        model = self.registry.parcel_model("12345678901234")
        self.assertIsNotNone(model)
        self.assertEqual(model["parent_ulpin"], "12345678901234")
        self.assertEqual(model["summary"]["registered_volumes"], 11)
        self.assertEqual(model["summary"]["rejected_proposals"], 2)
        self.assertTrue(all(feature["properties"]["ulpin3d"].startswith("12345678901234-") for feature in model["features"]))
        self.assertIsNone(self.registry.parcel_model("99999999999999"))
        with self.assertRaisesRegex(ProposalValidationError, "14 digits"):
            self.registry.parcel_model("123")

    def test_new_ulpin_is_available_after_approval(self):
        custom = proposal("99999999999999-P3D-123456ABCDEF", [-4, -3, 4, 3, 0, 3])
        custom["parent_ulpin"] = "99999999999999"
        custom["address"] = "42 New Market Road, Pune"
        custom["unit"] = "Office 8B"
        self.registry.submit(custom)
        self.registry.decide(custom["id"], "APPROVED", "DEMO-OFFICER", "Administrative demo waiver")
        model = self.registry.parcel_model("99999999999999")
        self.assertEqual(model["summary"]["registered_volumes"], 1)
        self.assertEqual(model["features"][0]["properties"]["key"], "Office 8B")

    def test_audit_chain_detects_database_tampering(self):
        self.registry.submit(proposal())
        self.registry.decide(proposal()["id"], "REJECTED", "DEMO-OFFICER")
        self.assertTrue(self.registry.verify_audit_chain())
        with closing(sqlite3.connect(self.registry.database)) as connection, connection:
            connection.execute("UPDATE audit_events SET detail_json = ? WHERE sequence = 1", ('{"changed":true}',))
        self.assertFalse(self.registry.verify_audit_chain())


if __name__ == "__main__":
    unittest.main()
