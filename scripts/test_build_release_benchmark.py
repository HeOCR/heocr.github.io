"""Exercise the release renderer without using evaluation results."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import benchmark_release_data as release
import build_release_benchmark as builder


def example():
    rows = [
        {
            "reader": f"Example Reader {index}",
            "metrics": {"cer": {"percent": 4, "ci95": [2, 6], "denominator": 100}},
        }
        for index in range(1, 11)
    ]
    carriers = {
        "fixture_scan": {"en": "Fixture scan", "he": "סריקה לדוגמה"},
        "fixture_phone": {"en": "Fixture phone", "he": "טלפון לדוגמה"},
    }
    return {
        "schema": release.SCHEMA,
        "p_mod_open": {
            "public_pages": 30,
            "carriers": carriers,
            "views": [
                {"name": name, "results": {key: rows[:] for key in carriers}}
                for name in ({"en": "Fixture full", "he": "מלא לדוגמה"}, {"en": "Fixture subset", "he": "חלקי לדוגמה"})
            ],
        },
        "uc_w": {"pages": 2, "results": rows[:1]},
    }


class ReleaseBuilderTest(unittest.TestCase):
    def test_layout_and_accessible_tables(self):
        data = example()
        release.validate(data)
        for lang, t in builder.T.items():
            output = builder.page(lang, data)
            opened, closed = output.split('id="closed"', 1)
            for part in (opened, closed):
                indices = [part.index(category) for category in t["categories"]]
                self.assertEqual(indices, sorted(indices))
            self.assertEqual(opened.count("Example Reader 10"), 4)
            self.assertEqual(opened.count('role="region"'), 4)
            self.assertEqual(closed.count("Example Reader "), 1)
            self.assertIn(t["published"].format(public=30, registered=31), opened)
            self.assertNotIn("launch conditions", output.lower())
            self.assertIn(builder.DATASET, opened)

    def test_layout_preview_has_no_release_data_or_dataset_link(self):
        for lang in builder.T:
            output = builder.page(lang, None)
            self.assertIn(builder.T[lang]["preview"], output)
            self.assertNotIn(builder.DATASET, output)
            self.assertNotIn('id="p-mod-open"', output)
            self.assertNotIn('id="uc-w"', output)

    def test_rejects_missing_carrier_and_mismatched_readers(self):
        data = example()
        del data["p_mod_open"]["views"][1]["results"]["fixture_scan"]
        with self.assertRaisesRegex(ValueError, "carrier coverage"):
            release.validate(data)
        data = example()
        data["p_mod_open"]["views"][1]["results"]["fixture_scan"][0] = {
            "reader": "Different fixture reader", "metrics": data["uc_w"]["results"][0]["metrics"],
        }
        with self.assertRaisesRegex(ValueError, "reader panel"):
            release.validate(data)

    def test_rejects_other_closed_fields(self):
        data = example()
        data["uc_w"]["metadata"] = "invented closed metadata"
        with self.assertRaisesRegex(ValueError, "uc_w"):
            release.validate(data)

    def test_validates_the_file_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.json"
            raw = json.dumps(example()).encode("utf-8")
            path.write_bytes(raw)
            self.assertEqual(release.load(path, hashlib.sha256(raw).hexdigest()), example())
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                release.load(path, "0" * 64)


if __name__ == "__main__":
    unittest.main()
