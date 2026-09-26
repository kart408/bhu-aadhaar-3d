import unittest

from packages.reconciliation import reconcile


class ReconciliationTests(unittest.TestCase):
    def test_clear_records(self):
        units = [
            {"volume_key": "A", "declared_carpet_m2": 50, "share_pct": 50},
            {"volume_key": "B", "declared_carpet_m2": 50, "share_pct": 50},
        ]
        rights = [
            {"volume_key": "A", "type": "ownership", "deed_ref": "D1", "active": True},
            {"volume_key": "B", "type": "ownership", "deed_ref": "D2", "active": True},
        ]
        report = reconcile(units, rights, {"A": 50, "B": 50})
        self.assertEqual(report["status"], "CLEAR")
        self.assertEqual(report["finding_count"], 0)

    def test_all_three_fault_types(self):
        units = [
            {"volume_key": "A", "declared_carpet_m2": 60, "share_pct": 55},
            {"volume_key": "B", "declared_carpet_m2": 50, "share_pct": 48},
        ]
        rights = [
            {"volume_key": "A", "type": "ownership", "deed_ref": "D1", "active": True},
            {"volume_key": "A", "type": "ownership", "deed_ref": "D2", "active": True},
        ]
        report = reconcile(units, rights, {"A": 50, "B": 50})
        self.assertEqual(report["status"], "FLAGGED")
        self.assertEqual(
            {finding["rule"] for finding in report["findings"]},
            {"SHARE_TOTAL", "AREA_MISMATCH", "DUPLICATE_ACTIVE_RIGHT"},
        )

    def test_inactive_historic_right_is_not_duplicate(self):
        units = [{"volume_key": "A", "declared_carpet_m2": 50, "share_pct": 100}]
        rights = [
            {"volume_key": "A", "type": "ownership", "deed_ref": "OLD", "active": False},
            {"volume_key": "A", "type": "ownership", "deed_ref": "NEW", "active": True},
        ]
        report = reconcile(units, rights, {"A": 50})
        self.assertEqual(report["status"], "CLEAR")


if __name__ == "__main__":
    unittest.main()

