import random
import unittest

from packages.ulpin3d import decode, encode, overlaps, validate


class CodecTests(unittest.TestCase):
    def test_known_round_trip(self):
        code = encode("12345678901234", 500010, 1450005, 500000, 1450000, 12, 15)
        decoded = decode(code)
        self.assertTrue(validate(code))
        self.assertEqual(decoded.parcel_ulpin, "12345678901234")
        self.assertEqual((decoded.de, decoded.dn), (10.0, 5.0))
        self.assertEqual((decoded.floor_h, decoded.ceil_h), (12.0, 15.0))

    def test_random_round_trips(self):
        random.seed(26011)
        for _ in range(10_000):
            de = random.uniform(-255.7, 255.2)
            dn = random.uniform(-255.7, 255.2)
            floor = random.uniform(-255.7, 255.2)
            height = random.uniform(0.3, 100)
            code = encode("12345678901234", de, dn, 0, 0, floor, floor + height)
            decoded = decode(code)
            self.assertLessEqual(abs(decoded.de - de), 0.25)
            self.assertLessEqual(abs(decoded.dn - dn), 0.25)
            self.assertLessEqual(abs(decoded.floor_h - floor), 0.25)
            self.assertLessEqual(abs((decoded.ceil_h - decoded.floor_h) - height), 0.25)

    def test_changed_character_breaks_checksum(self):
        code = encode("12345678901234", 10, 5, 0, 0, 12, 15).replace("-", "")
        replacement = "1" if code[17] != "1" else "2"
        changed = code[:17] + replacement + code[18:]
        self.assertFalse(validate(changed))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            encode("ABC", 0, 0, 0, 0, 0, 3)
        with self.assertRaises(ValueError):
            encode("12345678901234", 300, 0, 0, 0, 0, 3)
        with self.assertRaises(ValueError):
            encode("12345678901234", 0, 0, 0, 0, 3, 3)

    def test_overlap_screening(self):
        a = encode("12345678901234", 0, 0, 0, 0, 3, 6)
        b = encode("12345678901234", 2, 2, 0, 0, 4, 7)
        c = encode("12345678901234", 2, 2, 0, 0, 7, 10)
        self.assertTrue(overlaps(a, b, (6, 6), (6, 6)))
        self.assertFalse(overlaps(a, c, (6, 6), (6, 6)))


if __name__ == "__main__":
    unittest.main()

