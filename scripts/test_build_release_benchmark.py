"""Exercise the release renderer without using evaluation results."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import benchmark_release_data as release
import build_release_benchmark as builder


def example():
    names = [{"id": f"example-{index}", "label": f"Example Reader {index}"} for index in range(1, 11)]
    rows = [
        {"reader": name["id"], "cer": 0, "chars": 100, "edits": 0, "wer": 0, "words": 50,
         "word_edits": 0, "missed_numbers": 0, "ref_numbers": 2}
        for name in names
    ]
    carrier_counts = dict(zip(release.CARRIER_IDS, (22, 1, 5, 2, 0, 8, 6)))
    groups = {
        carrier: {"carriers": count, "readers": copy.deepcopy(rows) if count else []}
        for carrier, count in carrier_counts.items()
    }
    return {
        "schema": release.SCHEMA,
        "readers": names,
        "modern_print": {
            "aggregate_sha256": "0" * 64, "carriers": 22, "category_order": 1, "dataset": "Fixture",
            "issue_clusters": 3, "line_cer": None, "metric": "page_cer", "pages": 17, "score_scope": "Fixture",
            "view_labels": {"all": "Fixture all", "filtered": "Fixture subset"},
            "views": {"all": groups, "filtered": copy.deepcopy(groups)},
        },
        "welfare_reports": {
            "benchmark": "Fixture closed aggregate", "field_value_occurrences": 10, "metric": "field_recall_pct",
            "paddle_status": "Fixture", "page_cer": None, "pages": 2, "reports": 1, "score_scope": "Fixture",
            "readers": [{"reader": "example-1", "hits": 9, "field_recall_pct": 90, "ci95": [70, 100]}],
        },
    }


class ReleaseBuilderTest(unittest.TestCase):
    def test_layout_and_accessible_tables(self):
        data = release.validate(example())
        for lang, t in builder.T.items():
            output = builder.page(lang, data, public_pages=16)
            opened, closed = output.split('id="closed"', 1)
            for part in (opened, closed):
                indices = [part.index(category) for category in t["categories"]]
                self.assertEqual(indices, sorted(indices))
            self.assertEqual(opened.count("Example Reader 10"), 12)
            self.assertEqual(opened.count('role="region"'), 12)
            self.assertIn(t["carrier_count"].format(carriers=0), opened)
            self.assertEqual(closed.count("Example Reader "), 1)
            self.assertIn("90.00%", closed)
            self.assertIn(t["published"].format(public=16, registered=17), opened)
            self.assertNotIn("launch conditions", output.lower())
            self.assertIn(builder.DATASET, opened)

    def test_layout_preview_and_pending_rights(self):
        data = release.validate(example())
        for lang in builder.T:
            layout = builder.page(lang, None)
            self.assertIn(builder.T[lang]["preview"], layout)
            self.assertNotIn('id="uc-w"', layout)
            populated = builder.page(lang, data)
            self.assertIn(builder.T[lang]["scope_pending"], populated)
            self.assertIn('id="uc-w"', populated)
            self.assertNotIn(builder.DATASET, populated)

    def test_rejects_missing_carrier_and_mismatched_readers(self):
        raw = example()
        del raw["modern_print"]["views"]["filtered"]["archive"]
        with self.assertRaisesRegex(ValueError, "carrier coverage"):
            release.validate(raw)
        raw = example()
        raw["readers"].append({"id": "example-other", "label": "Different fixture reader"})
        raw["modern_print"]["views"]["filtered"]["archive"]["readers"][0]["reader"] = "example-other"
        with self.assertRaisesRegex(ValueError, "reader panel"):
            release.validate(raw)

    def test_rejects_other_closed_fields(self):
        raw = example()
        raw["welfare_reports"]["metadata"] = "invented closed metadata"
        with self.assertRaisesRegex(ValueError, "closed aggregate"):
            release.validate(raw)

    def test_validates_the_file_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.json"
            raw = json.dumps(example()).encode("utf-8")
            path.write_bytes(raw)
            self.assertEqual(release.load(path, hashlib.sha256(raw).hexdigest()), release.validate(example()))
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                release.load(path, "0" * 64)


if __name__ == "__main__":
    unittest.main()
