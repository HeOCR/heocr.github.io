import unittest

import build_leaderboard as builder
from leaderboard_results import BASELINES, DATASET, MANIFEST, SCHEMA, STRATA, validate


def fixture():
    views = {}
    for key, numerator in (("filtered", 1), ("all", 2)):
        views[key] = {name: {"edits": 0, "chars": 0} for name in STRATA}
        views[key]["pooled"] = views[key]["scanner"] = {"edits": numerator, "chars": 100}
    rows = [
        {"id": name, "category": "C1", "reader": f"<Fixture {name}>", "version": "1",
         "type": "open weights", "licence": "CC0-1.0", "date": "2026-11-24",
         "scorer_version": "fixture", "verified": True, "submission_sha256": None, "views": views}
        for name in sorted(BASELINES)
    ]
    return {"schema": SCHEMA, "benchmark": {"dataset": DATASET, "manifest_sha256": MANIFEST,
                                           "pages": 31, "carriers": 65}, "rows": rows}


class LeaderboardTest(unittest.TestCase):
    def test_both_languages_render_safe_labels_and_both_views(self):
        for lang in ("he", "en"):
            page = builder.page(lang, validate(fixture()))
            self.assertIn("1.00%", page)
            self.assertIn("2.00%", page)
            self.assertEqual(page.count('scope="row"'), 6)
            self.assertIn("&lt;Fixture tessdata-fast&gt;", page)
            self.assertNotIn("<Fixture", page)
            self.assertIn('id="C6"', page)
            other = "../leaderboard.html" if lang == "en" else "en/leaderboard.html"
            self.assertIn(f'href="{other}"', page)

    def test_missing_baseline_cannot_render(self):
        data = fixture()
        data["rows"].pop()
        with self.assertRaisesRegex(ValueError, "baselines"):
            validate(data)


if __name__ == "__main__":
    unittest.main()
