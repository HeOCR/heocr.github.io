"""Build bilingual benchmark release pages in a local staging directory."""
from __future__ import annotations

import argparse
import html
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import benchmark_release_data
import build_methodology
import shell

ROOT = Path(__file__).resolve().parents[1]
e = html.escape
DATASET = "https://huggingface.co/datasets/HeOCR/p-mod-open-v0"
T = {
    "en": {
        "title": "HeOCR benchmarks", "lede": "Real-world held-out benchmarks, with open sets first.",
        "open": "Open held-out sets", "open_text": "Open sets are designed so others can evaluate their readers independently.",
        "closed": "Closed held-out sets", "closed_text": "Closed sets may include private sources. They will also be reported, but cannot be independently reproduced in full.",
        "category": "Category", "result": "Held-out result", "missing": "Not measured on a held-out set yet",
        "categories": [
            "Modern printed, unpointed",
            "Modern printed, pointed",
            "Modern printed (weighted)",
            "Historical printed, unpointed",
            "Historical printed, pointed",
            "Historical printed (weighted)",
            "Historical handwriting",
            "Modern handwriting",
            "Handwriting (weighted)",
        ],
        "method": "Read the benchmark methodology", "preview": "Layout preview. Release figures are pending.",
        "open_result": "P-mod-open v0 results", "dataset": "Download the benchmark dataset", "doi": "Cite the dataset (Zenodo DOI)", "closed_missing": "No figure published here",
        "scope_pending": "The public dataset scope is pending source-rights review. The figures use the registered scope.",
        "carrier_count": "{carriers} images", "published": "The public dataset includes {public} of the {registered} scored pages. The figures use the registered scope.",
        "numbers": "Numbers missed",
        "views": {"all": "All captures", "filtered": "Filtered view"},
        "filtered_note": "Includes positions verified independently with no known overlap with project training.",
        "by_capture": "By capture type",
        "phone_note": "Phone A and Phone B are two phones that photographed the same pages.",
        "modern_intro": "{pages} pages of modern unpointed Hebrew, mostly legal notices and gazettes, across {carriers} images from archives, publishers, a scanner, and two phones.",
        "primary_cer": "The primary metric is page character error rate (CER). Lower is better.",
        "category_index": "Browse all categories",
        "closed_nav": "Closed sets",
        "commercial": "Additional API comparisons",
        "commercial_note": "The APIs were measured separately on 56 images with the original scored pixels and nine with artwork masked for public release.",
        "api_original": "56 images with the original scored pixels",
        "api_masked": "9 images with artwork masked",
        "gemini_note": "Gemini’s model family helped build the v0 references and may have an advantage.",
        "haiku_note": "Haiku 4.5 hit its output limit on 11 images.",
        "historical_intro": "Public-domain scans of historical unpointed Hebrew print. The set contains {leaves} leaves, {regions} image regions, and {lines} reference lines.",
        "historical_scope": "The deciding views use {eligible} eligible lines and {filtered} lines after excluding known training-text overlap.",
        "historical_all": "All eligible",
        "all_positions": "All positions",
        "historical_filtered": "Filtered",
        "historical_pooled": "Pooled results",
        "historical_result": "{model} had the lowest CER among the registered comparators in both deciding views.",
        "historical_caveat": "HeOCR P-hist v1.1 is a fine-tune of Rivok Full. The v0.1 references came from two independent AI transcriptions and adjudication. A re-score with human-proofread references is coming.",
        "descriptive": "Descriptive",
        "cloud_note": "Google’s descriptive scores use the same eligible and filtered lines. The registered result was decided before these comparisons.",
        "wer_all": "Word error (all)",
        "primary": "Primary",
        "best": "Lowest error",
        "ours": "HeOCR model",
        "carriers": {"archive": "Archive", "issuer-render": "Publisher PDF render", "issuer-scan": "Publisher scan", "scanner": "Scanner", "phone-a": "Phone A", "phone-b": "Phone B"},
        "reader": "Reader", "cer": "CER", "wer": "Word error rate",
    },
    "he": {
        "title": "מדדי ביצועים של HeOCR", "lede": "מבחנים על נתונים אמיתיים שהוחזקו בצד, עם הקבוצות הפתוחות תחילה.",
        "open": "קבוצות פתוחות שהוחזקו בצד", "open_text": "קבוצות פתוחות נועדו לאפשר הערכה עצמאית של מנועי זיהוי.",
        "closed": "קבוצות סגורות שהוחזקו בצד", "closed_text": "קבוצות סגורות עשויות לכלול מקורות פרטיים. גם תוצאותיהן ידווחו, אך לא ניתן לשחזר אותן במלואן באופן עצמאי.",
        "category": "קטגוריה", "result": "תוצאה על קבוצה מוחזקת בצד", "missing": "עוד לא נמדד על קבוצה מוחזקת בצד",
        "categories": [
            "דפוס מודרני ללא ניקוד",
            "דפוס מודרני מנוקד",
            "דפוס מודרני (משוקלל)",
            "דפוס היסטורי ללא ניקוד",
            "דפוס היסטורי מנוקד",
            "דפוס היסטורי (משוקלל)",
            "כתב יד היסטורי",
            "כתב יד מודרני",
            "כתב יד (משוקלל)",
        ],
        "method": "לשיטת בניית המבחנים", "preview": "תצוגה מקדימה של המבנה. נתוני ההערכה יתווספו לקראת הפרסום.",
        "open_result": "תוצאות P-mod-open v0", "dataset": "להורדת מערך המבחן", "doi": "ציטוט מערך הנתונים (Zenodo DOI)", "closed_missing": "אין כאן תוצאה שפורסמה",
        "scope_pending": "היקף מערך הנתונים הציבורי ייקבע לאחר בדיקת זכויות המקור. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "carrier_count": "{carriers} תמונות", "published": "מערך הנתונים הציבורי כולל {public} מתוך {registered} העמודים שהוערכו. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "numbers": "מספרים שלא זוהו",
        "views": {"all": "כל התמונות", "filtered": "תוצאות לאחר סינון"},
        "filtered_note": "מיקומים שאומתו באופן עצמאי ושאין להם חפיפה ידועה עם נתוני האימון של הפרויקט.",
        "by_capture": "לפי סוג הלכידה",
        "phone_note": "טלפון א׳ וטלפון ב׳ הם שני מכשירים שונים שצילמו את אותם העמודים.",
        "modern_intro": "{pages} עמודים של דפוס עברי מודרני ללא ניקוד, בעיקר מתוך רשומות והודעות משפטיות, ב־{carriers} תמונות מארכיונים, מגופים מפרסמים, מסורק ומשני טלפונים.",
        "primary_cer": "המדד הראשי הוא שיעור שגיאות התווים בעמוד (CER). ככל שהוא נמוך יותר, התוצאה טובה יותר.",
        "category_index": "כל הקטגוריות",
        "closed_nav": "קבוצות סגורות",
        "commercial": "השוואות נוספות לשירותי זיהוי",
        "commercial_note": "השירותים נבדקו בנפרד על 56 תמונות שבהן הפיקסלים זהים לאלה שנמדדו במקור, ועל תשע תמונות שבהן הוסתרו סמלים לקראת הפרסום.",
        "api_original": "56 תמונות עם הפיקסלים המקוריים",
        "api_masked": "9 תמונות עם סמלים מוסתרים",
        "gemini_note": "מודל מאותה משפחה של Gemini השתתף בהכנת טקסטי הייחוס של v0, ולכן ייתכן שיש לו יתרון.",
        "haiku_note": "Haiku 4.5 הגיע למגבלת אורך התשובה ב־11 תמונות.",
        "historical_intro": "סריקות ברשות הציבור של דפוס עברי היסטורי ללא ניקוד. הקבוצה כוללת {leaves} דפים, {regions} אזורים בתמונות ו־{lines} שורות ייחוס.",
        "historical_scope": "התוצאה נקבעת לפי שתי קבוצות שורות: {eligible} שורות כשירות ו־{filtered} שורות לאחר הסרת חפיפה ידועה עם טקסטי האימון.",
        "historical_all": "כולן",
        "all_positions": "כל המיקומים",
        "historical_filtered": "לאחר סינון",
        "historical_pooled": "תוצאות מצטברות",
        "historical_result": "ל־{model} היה שיעור שגיאות התווים הנמוך ביותר מבין המנועים שנרשמו מראש, בשתי קבוצות השורות.",
        "historical_caveat": "HeOCR P-hist v1.1 מבוסס על כוונון נוסף של Rivok Full. טקסטי הייחוס של v0.1 הוכנו בשני תעתוקים עצמאיים באמצעות בינה מלאכותית ובהכרעה ביניהם. בהמשך נחשב את הציונים שוב לפי טקסטי ייחוס שעברו הגהה אנושית.",
        "descriptive": "תיאורי",
        "cloud_note": "הציונים התיאוריים של Google חושבו על אותן שורות כשירות ומסוננות. התוצאה הרשומה נקבעה לפני ההשוואות האלה.",
        "wer_all": "שגיאות מילים (כולן)",
        "primary": "ראשי",
        "best": "שיעור השגיאות הנמוך ביותר",
        "ours": "מודל HeOCR",
        "carriers": {"archive": "ארכיון", "issuer-render": "תמונה מתוך PDF של הגוף המפרסם", "issuer-scan": "סריקה של הגוף המפרסם", "scanner": "סורק", "phone-a": "טלפון א׳", "phone-b": "טלפון ב׳"},
        "reader": "מנוע זיהוי", "cer": "CER", "wer": "שגיאות מילים",
    },
}


def category_table(t, scored_links=None, *, missing=None, preview=False):
    rows = []
    missing = "—" if preview else e(missing or t["missing"])
    for index, name in enumerate(t["categories"]):
        result = (scored_links or {}).get(index, missing)
        rows.append(f'<tr><th scope="row">{e(name)}</th><td>{result}</td></tr>\n')
    return (
        f'<div class="tablewrap"><table><thead><tr><th scope="col">{e(t["category"])}</th>'
        f'<th scope="col">{e(t["result"])}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>\n'
    )


def numbers(value):
    return f'<bdi dir="ltr">{value}</bdi>'


def error_rate(edits, denominator, *, as_count=False):
    if denominator == 0:
        return None, "—"
    value = Fraction(edits, denominator)
    if as_count:
        return value, numbers(f"{edits:,} / {denominator:,}")
    return value, numbers(f"{Decimal(edits) * 100 / denominator:.2f}%")


def result_table(t, heading_id, caption, columns, rows, *, level=4):
    # A table always uses column zero as the primary metric. Compare the exact
    # ratios so rounding percentages for display does not change the ranking.
    def order(row):
        value = row["cells"][0][0]
        return value is None, value, row["name"].casefold()

    best = [
        min((row["cells"][i][0] for row in rows if row["cells"][i][0] is not None), default=None)
        for i in range(len(columns))
    ]
    headers = "".join(
        f'<th scope="col">{e(column)}'
        + (f'<span class="benchmark-primary">{e(t["primary"])}</span>' if i == 0 else "")
        + '</th>'
        for i, column in enumerate(columns)
    )
    body = []
    for row in sorted(rows, key=order):
        ours = row.get("ours", False)
        marker = t["ours"] if ours else t["descriptive"] if row.get("descriptive") else None
        label = f'<bdi>{e(row["name"])}</bdi>'
        if marker:
            label += f'<small class="benchmark-reader-note">{e(marker)}</small>'
        cells = []
        for (value, formatted), lowest in zip(row["cells"], best, strict=True):
            if value is not None and value == lowest:
                formatted = f'<strong class="benchmark-best">{formatted}<span class="benchmark-sr-only"> ({e(t["best"])})</span></strong>'
            cells.append(f'<td class="num">{formatted}</td>')
        row_class = ' class="ours"' if ours else ""
        body.append(f'<tr{row_class}><th scope="row">{label}</th>{"".join(cells)}</tr>')
    return (
        f'<h{level} id="{heading_id}">{e(caption)}</h{level}>'
        f'<div class="tablewrap benchmark-table" role="region" tabindex="0" aria-labelledby="{heading_id}">'
        f'<table><thead><tr><th scope="col">{e(t["reader"])}</th>{headers}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>\n'
    )


def link(target, label):
    return f'<a href="{e(target)}">{e(label)}</a>'


def disclosure(summary, content, *, identifier=None):
    attr = f' id="{identifier}"' if identifier else ""
    return (f'<details class="method benchmark-details"{attr}><summary>{e(summary)}</summary>'
            f'<div class="benchmark-details-body">{content}</div></details>\n')


def score_cells(row):
    return [
        error_rate(row["edits"], row["chars"]),
        error_rate(row["word_edits"], row["words"]),
        error_rate(row["missed_numbers"], row["ref_numbers"], as_count=True),
    ]


def best_modern_model(data):
    # Keep the pooled winner fixed across all views and captures. The stock
    # pipeline is a baseline, so only choose among trained HeOCR models.
    candidates = [
        row for row in data["views"]["all"]["pooled"]["readers"]
        if row["reader_id"].startswith("heocr-") and row["reader_id"] != "heocr-stock"
    ]
    winner = min(candidates, key=lambda row: Fraction(row["edits"], row["chars"]), default=None)
    return winner["reader_id"] if winner is not None else None


def modern_table(t, heading, title, group, winner, *, level=4):
    rows = [
        {"name": "HeOCR Modern v1" if row["reader_id"] == "heocr-modern-1" else row["reader"],
         "ours": row["reader_id"] == winner, "cells": score_cells(row)}
        for row in group["readers"]
        if not row["reader_id"].startswith("heocr-") or row["reader_id"] == winner
    ]
    return result_table(t, heading, title, (t["cer"], t["wer"], t["numbers"]), rows, level=level)


def modern_api_results(t, api_rows):
    metrics = (f'{t["cer"]} · {t["all_positions"]}', f'{t["cer"]} · {t["historical_filtered"]}')

    def table(masked, heading, title):
        rows = []
        for row in api_rows:
            views = row["diagnostic"]["masked_views"] if masked else row["views"]
            counts = (views[view]["pooled"] for view in ("all", "filtered"))
            rows.append({"name": row["reader"],
                         "cells": [error_rate(count["edits"], count["chars"]) for count in counts]})
        return result_table(t, heading, title, metrics, rows)

    return disclosure(t["commercial"], "".join([
        f'<p>{e(t["commercial_note"])}</p>',
        table(False, "p-mod-open-api-original", t["api_original"]),
        table(True, "p-mod-open-api-masked", t["api_masked"]),
        f'<p class="note">{e(t["gemini_note"])} {e(t["haiku_note"])}</p>',
    ]), identifier="p-mod-open-api")


def open_results(t, data, public_pages, api_rows):
    out = [
        f'<article class="benchmark-result" id="p-mod-open"><h3><bdi>{e(t["open_result"])}</bdi></h3>',
        f'<p class="benchmark-intro">{e(t["modern_intro"].format(**data))}</p>',
        f'<p class="note">{e(t["primary_cer"])}</p>',
    ]
    if public_pages is None:
        out.append(f'<p class="note">{e(t["scope_pending"])}</p>')
    else:
        citation = link(benchmark_release_data.PMOD_OPEN_V0_DOI_URL, t["doi"])
        out.append(f'<p class="benchmark-links">{link(DATASET, t["dataset"])} · {citation}</p>')
        if public_pages != data["pages"]:
            note = t["published"].format(public=public_pages, registered=data["pages"])
            out.append(f'<p class="note">{e(note)}</p>')

    views = data["views"]
    winner = best_modern_model(data)
    out.append(modern_table(t, "p-mod-open-all-pooled", t["views"]["all"], views["all"]["pooled"], winner))
    filtered = modern_table(t, "p-mod-open-filtered-pooled", t["views"]["filtered"], views["filtered"]["pooled"], winner)
    out.append(disclosure(t["views"]["filtered"], f'<p>{e(t["filtered_note"])}</p>{filtered}'))

    captures = [f'<p>{e(t["phone_note"])}</p>']
    for view, groups in views.items():
        captures.append(f'<h4>{e(t["views"][view])}</h4>')
        for carrier in t["carriers"]:
            group = groups[carrier]
            if group["readers"]:
                title = f'{t["carriers"][carrier]} · {t["carrier_count"].format(carriers=group["carriers"])}'
                captures.append(modern_table(t, f"p-mod-open-{view}-{carrier}", title, group, winner, level=5))
    out.append(disclosure(t["by_capture"], "".join(captures), identifier="p-mod-open-captures"))
    if api_rows:
        out.append(modern_api_results(t, api_rows))
    out.append("</article>\n")
    return "".join(out)


def historical_results(t, data):
    rows = []
    for row in data["readers"]:
        all_cer, wer, missed = score_cells(row["all"])
        filtered_cer = error_rate(row["filtered"]["edits"], row["filtered"]["chars"])
        rows.append({"name": row["name"], "ours": row["id"].startswith("heocr-"),
                     "descriptive": row["descriptive"], "cells": [all_cer, filtered_cer, wer, missed]})
    model = next(row["name"] for row in rows if row["ours"])
    finding = e(t["historical_result"]).format(model=f"<bdi>{e(model)}</bdi>")
    columns = (
        f'{t["cer"]} · {t["historical_all"]}',
        f'{t["cer"]} · {t["historical_filtered"]}',
        t["wer_all"], t["numbers"],
    )
    return "".join([
        f'<article class="benchmark-result" id="p-hist-open"><h3><bdi>{e(data["dataset"])}</bdi></h3>',
        f'<p class="benchmark-intro">{e(t["historical_intro"].format(leaves=data["leaves"], regions=data["regions"], lines=data["reference_lines"]))}</p>',
        f'<p class="note">{e(t["primary_cer"])} {e(t["historical_scope"].format(eligible=data["eligible_lines"], filtered=data["filtered_lines"]))}</p>',
        f'<p class="benchmark-finding">{finding}</p>',
        result_table(t, "p-hist-open-pooled", t["historical_pooled"], columns, rows),
        f'<p class="note">{e(t["cloud_note"])}</p>',
        f'<p class="note">{e(t["historical_caveat"])}</p>',
        "</article>\n",
    ])


def page(lang, data, public_pages=None, *, historical=None, api_rows=()):
    t = T[lang]
    category_links = {}
    toc = []
    open_panels = []
    if data is not None:
        category_links[0] = link("#p-mod-open", t["open_result"])
        toc.append(("p-mod-open", e(t["categories"][0]), None))
        open_panels.append(open_results(t, data["open"], public_pages, api_rows))
    if historical is not None:
        category_links[3] = link("#p-hist-open", historical["dataset"])
        toc.append(("p-hist-open", e(t["categories"][3]), None))
        open_panels.append(historical_results(t, historical))
    if not toc:
        toc.append(("open", e(t["open"]), None))
    toc.append(("closed", e(t["closed_nav"]), None))
    preview_note = f'<p class="note">{e(t["preview"])}</p>' if data is None else ""
    return "".join([
        shell.head(lang, e(t["title"]), e(t["lede"]), "bench"), shell.header(lang, "bench"),
        '<main id="main" class="bench benchmark-page">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p><p>{link("methodology.html", t["method"])}</p>{preview_note}'),
        shell.toc(lang, toc),
        f'<section id="open" class="wrap domain"><h2>{e(t["open"])}</h2><p class="sub">{e(t["open_text"])}</p>',
        "".join(open_panels),
        disclosure(t["category_index"], category_table(t, category_links, preview=data is None)),
        "</section>\n",
        '<section id="closed" class="wrap domain">',
        disclosure(t["closed"], f'<p>{e(t["closed_text"])}</p>'
                   + category_table(t, missing=t["closed_missing"], preview=data is None)),
        "</section>\n",
        '</main>\n', shell.footer(['<p><a href="./">HeOCR</a></p>']), shell.tail(lang),
    ])


def write_pages(output_dir, data, public_pages, *, check, historical=None, api_rows=()):
    stale = []
    for lang in shell.LANGS:
        benchmark = page(lang, data, public_pages, historical=historical, api_rows=api_rows)
        for key, output in (("bench", benchmark), ("methodology", build_methodology.page(lang))):
            relative = shell.site_path(lang, key)
            path = output_dir / relative
            if check:
                if not path.is_file() or path.read_text(encoding="utf-8") != output:
                    stale.append(relative)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output, encoding="utf-8")
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--release-data", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--public-pages", type=int)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if (args.release_data is None) != (args.sha256 is None):
        parser.error("--release-data and --sha256 must be provided together")
    if args.public_pages is not None and args.release_data is None:
        parser.error("--public-pages requires --release-data")
    output_dir = args.out_dir.resolve()
    if output_dir.is_relative_to(ROOT):
        parser.error("--out-dir must be outside this site checkout")
    try:
        data = benchmark_release_data.load(args.release_data, args.sha256) if args.release_data else None
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.public_pages is not None and not 1 <= args.public_pages <= data["open"]["pages"]:
        parser.error("--public-pages exceeds the registered page scope or is zero")
    stale = write_pages(output_dir, data, args.public_pages, check=args.check)
    if stale:
        print("out of date: " + ", ".join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
