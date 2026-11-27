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
            self.assertNotIn('id="p-mod-open-all-issuer-scan"', opened)
            self.assertIn('<details class="method benchmark-details" id="p-mod-open-captures">', opened)
            self.assertIn(t["phone_note"], opened)
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
                            edits = (40, 20, 10)[index] if (view, carrier) == ("all", "pooled") else (10, 20, 5)[index]
                            row.update(reader=key, edits=edits, cer=release.Decimal(edits) / 100)
        raw["welfare_reports"]["readers"][0]["reader"] = names[0]["id"]
        for lang in builder.T:
            output = builder.page(lang, release.validate(raw))
            self.assertEqual(output.count('<tr class="ours">'), 12)
            self.assertEqual(output.count("Example best model"), 12)
            self.assertNotIn("Example stock pipeline", output)
            self.assertNotIn("Example slower model", output)
            self.assertEqual(output.count("Example Reader 4"), 12)

    def test_primary_order_and_independent_minima(self):
        rows = [
            {"name": "Slower", "cells": [builder.error_rate(4, 100), builder.error_rate(1, 10)]},
            {"name": "Faster", "ours": True,
             "cells": [builder.error_rate(3, 100), builder.error_rate(2, 10)]},
            {"name": "Tied", "cells": [builder.error_rate(3, 100), builder.error_rate(0, 0)]},
        ]
        t = builder.T["en"]
        table = builder.result_table(t, "fixture", "Fixture", ("CER", "WER"), rows)
        body = re.findall(r'<tr(?: class="ours")?><th scope="row">.*?</tr>', table)
        self.assertEqual([row.partition("<bdi>")[2].partition("</bdi>")[0] for row in body],
                         ["Faster", "Tied", "Slower"])
        self.assertRegex(body[0], 'class="benchmark-best"><bdi dir="ltr">3.00%')
        self.assertRegex(body[1], 'class="benchmark-best"><bdi dir="ltr">3.00%')
        self.assertRegex(body[2], 'class="benchmark-best"><bdi dir="ltr">10.00%')
        self.assertEqual(table.count('class="benchmark-best"'), 3)

    def test_historical_result_links_from_category_and_labels_api_lanes(self):
        score = {"edits": 2, "chars": 100, "word_edits": 1, "words": 10,
                 "missed_numbers": 0, "ref_numbers": 1}
        historical = {
            "dataset": "Fixture historical", "leaves": 2, "regions": 3, "reference_lines": 30,
            "eligible_lines": 28, "filtered_lines": 25,
            "readers": [
                {"id": "heocr-example", "name": "Example historical model", "descriptive": False,
                 "all": score, "filtered": score},
                {"id": "example-api", "name": "Example historical API", "descriptive": True,
                 "all": score, "filtered": score},
            ],
        }
        for lang, t in builder.T.items():
            output = builder.page(lang, release.validate(example()), historical=historical)
            self.assertIn(f'<th scope="row">{t["categories"][3]}</th>'
                          '<td><a href="#p-hist-open">Fixture historical</a></td>', output)
            panel = output.split('id="p-hist-open"', 1)[1].split("</article>", 1)[0]
            self.assertEqual(panel.count('<tr class="ours">'), 1)
            self.assertIn(f'<bdi>Example historical API</bdi><small class="benchmark-reader-note">{t["descriptive"]}</small>', panel)
            self.assertIn(t["historical_caveat"], panel)
            self.assertIn('href="methodology.html"', output)

    def test_public_phone_aliases_preserve_the_legacy_aggregate_rows(self):
        sample = example()
        data = release.validate(sample)
        for groups in sample["modern_print"]["views"].values():
            groups["iphone"] = groups.pop("phone-a")
            groups["pixel"] = groups.pop("phone-b")
        self.assertEqual(release.validate(sample), data)
        for lang in builder.T:
            output = builder.page(lang, data)
            self.assertIn('id="p-mod-open-all-phone-a"', output)
            self.assertIn('id="p-mod-open-filtered-phone-b"', output)
            self.assertNotIn("iphone", output.casefold())
            self.assertNotIn("pixel", output.casefold())

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
