import json
from pathlib import Path
import unittest

from packages.geometry import RectVolume, find_conflicts, validate_volume
from scripts.build_demo import build


ROOT = Path(__file__).resolve().parents[1]


class GeometryTests(unittest.TestCase):
    def test_touching_units_do_not_overlap(self):
        west = RectVolume("W", "unit", -10, -5, 0, 5, 0, 3)
        east = RectVolume("E", "unit", 0, -5, 10, 5, 0, 3)
        above = RectVolume("A", "unit", -10, -5, 0, 5, 3, 6)
        self.assertFalse(west.intersects(east))
        self.assertFalse(west.intersects(above))

    def test_positive_shared_volume_is_conflict(self):
        first = RectVolume("A", "unit", -10, -5, 1, 5, 0, 3)
        second = RectVolume("B", "unit", 0, -4, 10, 4, 1, 4)
        self.assertTrue(first.intersects(second))
        self.assertEqual(find_conflicts([first, second]), [("A", "B")])

    def test_parent_containment(self):
        parcel = RectVolume("P", "parcel", -20, -15, 20, 15, -10, 20)
        valid = RectVolume("V", "unit", -5, -5, 5, 5, 0, 3)
        invalid = RectVolume("I", "unit", 18, -5, 25, 5, 0, 3)
        self.assertEqual(validate_volume(valid, parcel), [])
        self.assertEqual(validate_volume(invalid, parcel), ["OUTSIDE_PARENT_PARCEL"])

    def test_seed_is_valid_and_bad_proposals_are_rejected(self):
        seed = json.loads((ROOT / "data/seed/demo_tower.json").read_text())
        geojson, report = build(seed)
        self.assertEqual(len(geojson["features"]), 13)
        rejected = [
            feature for feature in geojson["features"]
            if feature["properties"].get("registration_status") == "REJECTED"
        ]
        self.assertEqual(len(rejected), 2)
        self.assertEqual(report["registered_volume_count"], 11)
        self.assertTrue(report["all_registered_volumes_valid"])
        self.assertEqual(report["registered_conflicts"], [])
        results = {item["key"]: item for item in report["proposed_insert_results"]}
        self.assertIn("UNIT-302", results["BAD-DUPLICATE-302"]["conflicts_with"])
        self.assertIn("OUTSIDE_PARENT_PARCEL", results["BAD-OUTSIDE-501"]["validation_errors"])
        self.assertFalse(results["BAD-DUPLICATE-302"]["accepted"])
        self.assertFalse(results["BAD-OUTSIDE-501"]["accepted"])


if __name__ == "__main__":
    unittest.main()
