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
            self.assertEqual(page.count('scope="row"'), 10)
            self.assertIn("&lt;Fixture tessdata-fast&gt;", page)
            self.assertNotIn("<Fixture", page)
            self.assertIn('id="C6"', page)
            self.assertIn(f'href="{builder.SUBMIT}"', page)
            self.assertIn(f'href="{builder.SPACE}"', page)
            self.assertIn(f'href="{builder.PMOD_OPEN_V0_DOI_URL}"', page)
            other = "../leaderboard.html" if lang == "en" else "en/leaderboard.html"
            self.assertIn(f'href="{other}"', page)

    def test_vertex_scopes_remain_outside_ranking(self):
        import leaderboard_results as results

        data = results.read_results(builder.SITE / "leaderboard/results.json")
        row = next(row for row in data["rows"] if row["id"] == "gemini-vertex-v0")
        self.assertEqual(row["type"], "commercial API")
        self.assertEqual(row["views"]["filtered"]["pooled"], {"edits": 7921, "chars": 61212})
        self.assertEqual(row["views"]["all"]["pooled"], {"edits": 14378, "chars": 81161})
        self.assertEqual(row["diagnostic"]["masked_views"]["filtered"]["pooled"], {"edits": 2072, "chars": 9333})
        self.assertEqual(row["diagnostic"]["masked_views"]["all"]["pooled"], {"edits": 3238, "chars": 12567})
        self.assertNotIn(row, results.ranked(data, "filtered"))
        for lang in ("en", "he"):
            page = builder.page(lang, data)
            self.assertIn(results.BIAS_NOTICE, page)
            self.assertIn("<td>56</td>", page)
            self.assertIn("<td>9</td>", page)
            self.assertIn("12.94%", page)
            self.assertIn("22.20%", page)

    def test_api_diagnostics_render_separate_matched_and_masked_scores(self):
        from leaderboard_results import ARTWORK_MASK_NOTICE, read_results

        data = read_results(builder.SITE / "leaderboard/results.json")
        expected = {
            "Google Cloud Vision": ("16.35%", "13.59%"),
            "Google Document AI Enterprise OCR": ("18.46%", "14.61%"),
            "Claude Haiku 5.5": ("8.34%", "4.60%"),
        }
        for lang in ("en", "he"):
            with self.subTest(lang=lang):
                page = builder.page(lang, data)
                ranked_table = builder.table(data, "filtered", lang)
                for reader, (matched, masked) in expected.items():
                    diagnostic = page.split(f"<h3><bdi>{reader} ·", 1)[1].split("</section>", 1)[0]
                    self.assertIn("commercial API", diagnostic)
                    self.assertIn(ARTWORK_MASK_NOTICE, diagnostic)
                    self.assertIn(f"<td>56</td><td>{matched}</td>", diagnostic)
                    self.assertIn(f"<td>9</td><td>{masked}</td>", diagnostic)
                    self.assertNotIn(reader, ranked_table)

    def test_haiku45_discloses_the_output_cap_in_both_languages(self):
        from leaderboard_results import read_results

        data = read_results(builder.SITE / "leaderboard/results.json")
        for lang in ("en", "he"):
            with self.subTest(lang=lang):
                page = builder.page(lang, data)
                diagnostic = page.split("<h3><bdi>Claude Haiku 4.5 ·", 1)[1].split("</section>", 1)[0]
                self.assertIn("commercial API", diagnostic)
                self.assertIn("64/65 Haiku 4.5 replies were Hebrew-dominant", diagnostic)
                self.assertIn("1 Latin-dominant. 11 hit the output cap.", diagnostic)
                self.assertIn("<td>56</td><td>98.94%</td>", diagnostic)
                self.assertIn("<td>9</td><td>159.20%</td>", diagnostic)
                self.assertNotIn("Claude Haiku 4.5", builder.table(data, "filtered", lang))

    def test_submission_guide_and_unverified_row_are_bilingual(self):
        data = fixture()
        row = {**data["rows"][0], "id": "a" * 64, "submission_sha256": "a" * 64,
               "type": "closed weights", "verified": False}
        data["rows"].append(row)
        for lang, heading, status in (
            ("en", "How to submit", "Self-submitted, unverified"),
            ("he", "איך מגישים תוצאות?", "הוגש עצמאית, טרם אומת"),
        ):
            with self.subTest(lang=lang):
                page = builder.page(lang, validate(data))
                self.assertIn(f'id="how-to-submit"><h2>{heading}</h2>', page)
                self.assertIn(f'<bdi>{status}</bdi>', page)
                self.assertIn(f'href="{builder.SUBMIT}"', page)

    def test_efficiency_renders_each_host_and_distinguishes_api_prices(self):
        from leaderboard_results import read_results

        data = read_results(builder.SITE / "leaderboard/results.json")
        for lang in ("en", "he"):
            with self.subTest(lang=lang):
                panel = builder.efficiency(data, lang)
                self.assertEqual(panel.count('scope="row"'), 12)
                self.assertEqual(panel.count("<bdi>65 / 1</bdi>"), 5)
                self.assertEqual(panel.count("<bdi>65 / 3</bdi>"), 5)
                self.assertIn("<bdi>17.23</bdi>", panel)
                self.assertIn("<bdi>10.47</bdi>", panel)
                self.assertIn("ONNX", panel)
                self.assertIn("CUDA", panel)
                self.assertNotIn("PaddleOCR (CUDA)", panel)
                gemini = panel.split("<bdi>Gemini (Vertex)</bdi>")
                self.assertEqual(len(gemini), 3)
                for row in gemini[1:]:
                    self.assertEqual(row.split("</tr>", 1)[0].count("<bdi>—</bdi>"), 6)
                    self.assertIn("<bdi>0.75 / 3.75</bdi>", row.split("</tr>", 1)[0])

    def test_missing_baseline_cannot_render(self):
        data = fixture()
        data["rows"].pop()
        with self.assertRaisesRegex(ValueError, "baselines"):
            validate(data)


if __name__ == "__main__":
    unittest.main()
