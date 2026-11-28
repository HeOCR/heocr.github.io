"""Exercise the release renderer without using evaluation results."""

import copy
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

import benchmark_release_data as release
import build_release_benchmark as builder
import reader_access

UNKNOWN = '<span class="reader-access" data-access="unknown"></span>'


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
            self.assertEqual(opened.count("Example Reader 10"), 10)
            self.assertEqual(opened.count("<caption"), 10)
            self.assertIn('data-score-view value="filtered" checked', opened)
            self.assertIn('data-score-view value="all"', opened)
            self.assertIn('data-score-capture value="pooled" checked', opened)
            self.assertIn(t["all_images"].format(count=22), opened)
            self.assertNotIn('value="issuer-scan"', opened)
            self.assertNotIn('id="p-mod-open-all-issuer-scan"', opened)
            self.assertIn('<details class="method benchmark-details" id="p-mod-open-alternatives">', opened)
            self.assertIn('data-score-capture-note="phone" hidden', opened)
            self.assertIn(t["capture_notes"]["phone"], opened)
            self.assertIn(f'{t["carriers"]["phone"]} (13)', opened)
            self.assertNotIn('data-score-capture value="phone-a"', opened)
            self.assertNotIn('data-score-capture value="phone-b"', opened)
            self.assertIn(t["metric_help"]["cer"], opened)
            self.assertNotIn(t["in_progress"][0], opened)
            self.assertIn(t["in_progress"][0], closed)
            self.assertIn(t["more_sets"], closed)
            prefix = "" if lang == "he" else "../"
            self.assertIn(f'<script src="{prefix}benchmark-controls.js" defer>', output)
            self.assertNotIn("Example Reader ", closed)
            self.assertNotIn("90.00%", output)
            self.assertIn(t["closed_missing"], closed)
            self.assertIn(t["published"].format(public=16, registered=17), opened)
            self.assertNotIn("launch conditions", output.lower())
            self.assertIn(builder.DATASET, opened)

    def test_one_model_selected_by_pooled_cer_for_every_view(self):
        raw = example()
        names = raw["readers"]
        for index, (key, label) in enumerate((
            ("heocr-slower", "Example slower model"),
            ("heocr-winner", "Example best model"),
            ("heocr-stock", "Example stock pipeline"),
        )):
            old_id = names[index]["id"]
            names[index].update(id=key, label=label)
            for view, groups in raw["modern_print"]["views"].items():
                for carrier, group in groups.items():
                    for row in group["readers"]:
                        if row["reader"] == old_id:
                            edits = (40, 20, 10)[index] if (view, carrier) == ("filtered", "pooled") else (10, 20, 5)[index]
                            row.update(reader=key, edits=edits, cer=release.Decimal(edits) / 100)
        raw["welfare_reports"]["readers"][0]["reader"] = names[0]["id"]
        for lang in builder.T:
            output = builder.page(lang, release.validate(raw))
            self.assertEqual(output.count('<tr class="ours">'), 10)
            note = builder.T[lang]["modern_model_note"]
            self.assertEqual(output.count(f'<th scope="row"><bdi>Example best model</bdi>{UNKNOWN}'
                                          f'<small class="benchmark-reader-note">{note}</small></th>'), 10)
            self.assertNotIn("Example stock pipeline", output)
            self.assertNotIn("Example slower model", output)
            self.assertEqual(output.count("Example Reader 4"), 10)

    def test_primary_order_and_independent_minima(self):
        rows = [
            {"name": "Slower", "cells": [builder.error_rate(4, 100), builder.error_rate(1, 10)]},
            {"name": "Faster", "ours": True, "model_url": "download.html",
             "cells": [builder.error_rate(3, 100), builder.error_rate(2, 10)]},
            {"name": "Tied", "cells": [builder.error_rate(3, 100), builder.error_rate(0, 0)]},
        ]
        t = builder.T["en"]
        table = builder.result_table(t, "fixture", "Fixture", ("cer", "wer"), rows)
        body = re.findall(r'<tr(?: class="ours")?><th scope="row">.*?</tr>', table)
        self.assertEqual([row.partition("<bdi>")[2].partition("</bdi>")[0] for row in body],
                         ["Faster", "Tied", "Slower"])
        self.assertRegex(body[0], 'class="benchmark-best"><bdi dir="ltr">3.00%')
        self.assertRegex(body[1], 'class="benchmark-best"><bdi dir="ltr">3.00%')
        self.assertRegex(body[2], 'class="benchmark-best"><bdi dir="ltr">10.00%')
        self.assertEqual(table.count('class="benchmark-best"'), 3)
        self.assertIn('<small class="benchmark-fraction"><bdi dir="ltr">3 / 100</bdi></small>', body[0])
        self.assertIn('<td class="num">—</td>', body[1])

    def test_access_badges_and_lowest_open_highlight(self):
        rows = [
            {"name": "Google Cloud Vision", "cells": [builder.error_rate(1, 100), builder.error_rate(1, 10)]},
            {"name": "HeOCR modern MEASURED v1.0", "ours": True,
             "cells": [builder.error_rate(2, 100), builder.error_rate(1, 10)]},
            {"name": "Rivok Full", "cells": [builder.error_rate(3, 100), builder.error_rate(2, 10)]},
            {"name": "Google Drive built-in OCR", "cells": [(None, ""), (None, "")]},
        ]
        for lang in builder.T:
            table = builder.result_table(builder.T[lang], "fixture", "Fixture", ("cer", "wer"), rows)
            body = re.findall(r'<tr(?: class="ours")?><th scope="row">.*?</tr>', table)
            self.assertIn('data-access="paid"', body[0])
            self.assertIn('data-access="open"', body[1])
            self.assertIn('data-access="free_closed"', body[3])
            self.assertIn(reader_access.LABEL[lang]["open"], body[1])
            # CER: the paid reader is lowest overall; HeOCR is lowest among open readers.
            self.assertRegex(body[0], 'class="benchmark-best"><bdi dir="ltr">1.00%')
            self.assertRegex(body[1], 'class="benchmark-best-open"><bdi dir="ltr">2.00%')
            self.assertIn(reader_access.BEST_OPEN[lang], body[1])
            # WER: an open reader tied for lowest overall gets the overall highlight only.
            self.assertRegex(body[1], 'class="benchmark-best"><bdi dir="ltr">10.00%')
            self.assertEqual(table.count('class="benchmark-best-open"'), 1)
            self.assertNotIn("benchmark-best-open", body[2])

    def test_reader_classification_fails_closed(self):
        for name, kind in (("Tesseract heb best", "open"), ("Tessdata Fast Hebrew", "open"), ("Rivok Lite", "open"),
                           ("Rivok PaddleOCR", "open"), ("Kraken 7.2 (generic recognizer)", "open"),
                           ("PaddleOCR (CUDA)", "open"), ("Qwen3-VL-2B-Instruct MLX 4-bit", "open"),
                           ("HeOCR old-print v1.1", "open"), ("Google Document AI OCR", "paid"),
                           ("Gemini (Vertex)", "paid"), ("Claude Haiku 5.5", "paid"),
                           ("Google Drive built-in OCR", "free_closed")):
            self.assertEqual(reader_access.classify(name), kind, name)
        self.assertIsNone(reader_access.classify("Some new reader"))
        with self.assertRaises(ValueError):
            reader_access.check_classified(f"<tr><th>Some new reader{UNKNOWN}</th></tr>")
        for lang in builder.T:
            legend = reader_access.legend(lang)
            for kind in reader_access.KINDS:
                self.assertIn(reader_access.LEGEND[lang][kind], legend)
            self.assertIn("benchmark-best-open", legend)

    def test_historical_has_two_scope_choices_and_labels_api_lanes(self):
        score = {"edits": 2, "chars": 100, "word_edits": 1, "words": 10,
                 "missed_numbers": 1, "ref_numbers": 8}
        filtered = {**score, "edits": 1, "chars": 80, "word_edits": 2, "words": 8}
        historical = {
            "dataset": "Fixture historical", "leaves": 2, "regions": 3, "reference_lines": 30,
            "eligible_lines": 28, "filtered_lines": 25,
            "readers": [
                {"id": "heocr-p-hist-v1-1", "name": "Example historical model", "descriptive": False,
                 "all": score, "filtered": filtered},
                {"id": "example-api", "name": "Example historical API", "descriptive": True,
                 "all": score, "filtered": score},
            ],
        }
        for lang, t in builder.T.items():
            output = builder.page(lang, release.validate(example()), historical=historical)
            self.assertIn(f'<a href="#p-hist-open">{t["historical"]}</a>', output)
            panel = output.split('id="p-hist-open"', 1)[1].split("</article>", 1)[0]
            default, fallback = panel.split('id="p-hist-open-scores-alternatives"', 1)
            self.assertEqual(default.count('<tr class="ours">'), 1)
            self.assertEqual(fallback.count('<tr class="ours">'), 1)
            self.assertIn('id="p-hist-open-scores-filtered-pooled"', default)
            self.assertIn('id="p-hist-open-scores-all-pooled"', fallback)
            self.assertIn(f'<a href="{builder.HISTORICAL_MODEL}"><bdi>Example historical model</bdi></a>', default)
            self.assertIn('<bdi dir="ltr">2 / 8</bdi>', default)
            self.assertIn('<bdi dir="ltr">1 / 10</bdi>', fallback)
            self.assertIn(f'<bdi>Example historical API</bdi>{UNKNOWN}'
                          f'<small class="benchmark-reader-note">{t["descriptive"]}</small>', panel)
            self.assertNotIn(t["metric_help"]["numbers"], panel)
            self.assertNotIn('<bdi dir="ltr">1 / 8</bdi>', panel)
            self.assertIn(t["historical_numbers_note"], panel)
            self.assertIn(t["metric_help"]["numbers"], output.split('id="p-hist-open"', 1)[0])
            self.assertIn(t["historical_caveat"], panel)
            self.assertIn('href="methodology.html"', output)
            self.assertIn(t["region_count"].format(count=3), panel)
            self.assertIn(t["reference_count"].format(count=30), panel)
            self.assertIn(t["reading"], output)

    def test_public_phone_aliases_preserve_the_legacy_aggregate_rows(self):
        sample = example()
        data = release.validate(sample)
        for groups in sample["modern_print"]["views"].values():
            groups["iphone"] = groups.pop("phone-a")
            groups["pixel"] = groups.pop("phone-b")
        self.assertEqual(release.validate(sample), data)
        for lang in builder.T:
            output = builder.page(lang, data)
            self.assertIn('id="p-mod-open-all-phone"', output)
            self.assertIn('id="p-mod-open-filtered-phone"', output)
            self.assertNotIn("iphone", output.casefold())
            self.assertNotIn("pixel", output.casefold())

    def test_pools_each_metric_from_counts_by_reader(self):
        sample = example()
        groups = sample["modern_print"]["views"]["filtered"]
        groups["phone-a"]["readers"][0].update(edits=2, cer=release.Decimal("0.02"),
                                                     word_edits=4, wer=release.Decimal("0.08"),
                                                     missed_numbers=1)
        groups["phone-b"]["readers"][0].update(chars=300, edits=27, cer=release.Decimal("0.09"),
                                                     words=200, word_edits=40, wer=release.Decimal("0.20"),
                                                     ref_numbers=6, missed_numbers=2)
        groups["phone-b"]["readers"].reverse()
        data = release.validate(sample)
        output = builder.page("en", data)
        phone = output.split('id="p-mod-open-filtered-phone"', 1)[1].split("</table>", 1)[0]
        reader = phone.split("Example Reader 1</bdi>", 1)[1].split("</tr>", 1)[0]
        for score, fraction in (("7.25%", "29 / 400"), ("17.60%", "44 / 250"), ("37.50%", "3 / 8")):
            self.assertIn(score, reader)
            self.assertIn(fraction, reader)

    def test_layout_preview_and_pending_rights(self):
        data = release.validate(example())
        for lang in builder.T:
            layout = builder.page(lang, None)
            self.assertIn(builder.T[lang]["preview"], layout)
            self.assertNotIn('id="uc-w"', layout)
            populated = builder.page(lang, data)
            self.assertIn(builder.T[lang]["scope_pending"], populated)
            self.assertNotIn('id="uc-w"', populated)
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
