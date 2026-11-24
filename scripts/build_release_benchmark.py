"""Build bilingual benchmark release pages in a local staging directory."""
from __future__ import annotations

import argparse
import html
import sys
from decimal import Decimal
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
        "open": "Open held-out sets", "open_text": "Open sets make their images and references available for independent evaluation.",
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
        "open_result": "P-mod-open v0 results", "dataset": "Download the benchmark dataset", "closed_missing": "No figure published here",
        "pages": "{pages} registered pages · {carriers} scored carriers",
        "scope_pending": "The public dataset scope is pending source-rights review. The figures use the registered scope.",
        "carrier_count": "{carriers} carriers", "published": "The public dataset includes {public} of the {registered} scored pages. The figures use the registered scope.",
        "numbers": "Numbers missed",
        "views": {"all": "All reference positions", "filtered": "Common independently verified positions without known project training overlap"},
        "carriers": {"pooled": "All carriers", "archive": "Archive", "phone-a": "Phone A", "issuer-render": "Issuer render", "issuer-scan": "Issuer scan", "phone-b": "Phone B", "scanner": "Scanner"},
        "reader": "Reader", "cer": "Character error rate", "wer": "Word error rate",
        "lower": "Lower error rates are better.",
    },
    "he": {
        "title": "מדדי ביצועים של HeOCR", "lede": "מבחנים על נתונים אמיתיים שהוחזקו בצד, עם הקבוצות הפתוחות תחילה.",
        "open": "קבוצות פתוחות שהוחזקו בצד", "open_text": "קבוצות פתוחות מעמידות את התמונות וטקסטי הייחוס לרשות מי שרוצים לערוך הערכה עצמאית.",
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
        "open_result": "תוצאות P-mod-open v0", "dataset": "להורדת מערך המבחן", "closed_missing": "אין כאן תוצאה שפורסמה",
        "pages": "{pages} עמודים רשומים · {carriers} גרסאות מקור שנבדקו",
        "scope_pending": "היקף מערך הנתונים הציבורי ייקבע לאחר בדיקת זכויות המקור. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "carrier_count": "{carriers} גרסאות מקור", "published": "מערך הנתונים הציבורי כולל {public} מתוך {registered} העמודים שהוערכו. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "numbers": "מספרים שלא זוהו",
        "views": {"all": "כל המיקומים בטקסט הייחוס", "filtered": "מיקומים משותפים שאומתו באופן עצמאי וללא חפיפה ידועה לאימון הפרויקט"},
        "carriers": {"pooled": "כל גרסאות המקור", "archive": "ארכיון", "phone-a": "טלפון א׳", "issuer-render": "תצוגה ממוחשבת של הגוף המפרסם", "issuer-scan": "סריקה של הגוף המפרסם", "phone-b": "טלפון ב׳", "scanner": "סורק"},
        "reader": "מנוע זיהוי", "cer": "שיעור שגיאות תווים", "wer": "שיעור שגיאות מילים",
        "lower": "שיעור שגיאות נמוך יותר עדיף.",
    },
}


def category_table(t, scored_link="", *, missing=None, preview=False):
    rows = []
    missing = "—" if preview else e(missing or t["missing"])
    for index, name in enumerate(t["categories"]):
        result = scored_link if index == 0 and scored_link else missing
        rows.append(f'<tr><th scope="row">{e(name)}</th><td>{result}</td></tr>\n')
    return (
        f'<div class="tablewrap"><table><thead><tr><th scope="col">{e(t["category"])}</th>'
        f'<th scope="col">{e(t["result"])}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>\n'
    )


def numbers(value):
    return f'<bdi dir="ltr">{value}</bdi>'


def error_rate_cell(value, edits, denominator):
    percentage = numbers(f"{Decimal(value) * 100:.2f}%")
    counts = numbers(f"{edits:,} / {denominator:,}")
    return f'<td class="num"><span class="v">{percentage}</span><span class="tag-n block">{counts}</span></td>'


def result_table(t, heading_id, caption, level, columns, rows):
    headers = "".join(f'<th scope="col">{e(t[column])}</th>' for column in columns)
    body = "".join(f'<tr><th scope="row"><bdi>{e(reader)}</bdi></th>{cells}</tr>' for reader, cells in rows)
    return (
        f'<h{level} id="{heading_id}">{e(caption)}</h{level}>'
        f'<div class="tablewrap narrow" role="region" tabindex="0" aria-labelledby="{heading_id}">'
        f'<table><thead><tr><th scope="col">{e(t["reader"])}</th>{headers}</tr></thead>'
        f'<tbody>{body}</tbody></table></div>\n'
    )


def link(target, label):
    return f'<a href="{target}">{e(label)}</a>'


def open_rows(rows):
    for row in rows:
        cer = error_rate_cell(row["cer"], row["edits"], row["chars"])
        wer = error_rate_cell(row["wer"], row["word_edits"], row["words"])
        numeric = numbers(f'{row["missed_numbers"]:,} / {row["ref_numbers"]:,}')
        yield row["reader"], f'{cer}{wer}<td class="num">{numeric}</td>'


def open_results(t, data, public_pages):
    scope = e(t["pages"].format(pages=data["pages"], carriers=data["carriers"]))
    out = [f'<h3 id="p-mod-open">{e(t["open_result"])}</h3>']
    if public_pages is None:
        out.extend([f'<p>{scope}</p>', f'<p class="note">{e(t["scope_pending"])}</p>'])
    else:
        out.append(f'<p>{scope} · {link(DATASET, t["dataset"])}</p>')
        if public_pages != data["pages"]:
            note = t["published"].format(public=public_pages, registered=data["pages"])
            out.append(f'<p class="note">{e(note)}</p>')
    out.append(f'<p class="note">{e(t["lower"])}</p>')
    for view_id, groups in data["views"].items():
        heading = f"p-mod-open-{view_id}"
        out.append(f'<section aria-labelledby="{heading}"><h4 id="{heading}">{e(t["views"][view_id])}</h4>')
        for carrier, group in groups.items():
            title = f'{t["carriers"][carrier]} · {t["carrier_count"].format(carriers=group["carriers"])}'
            if group["readers"]:
                out.append(result_table(t, f"{heading}-{carrier}", title, 5, ("cer", "wer", "numbers"), open_rows(group["readers"])))
            else:
                out.append(f'<p class="note">{e(title)}</p>')
        out.append("</section>")
    return "".join(out)


def page(lang, data, public_pages=None):
    t = T[lang]
    open_link = link("#p-mod-open", t["open_result"]) if data is not None else ""
    open_panel = open_results(t, data["open"], public_pages) if data is not None else ""
    preview_note = f'<p class="note">{e(t["preview"])}</p>' if data is None else ""
    return "".join([
        shell.head(lang, e(t["title"]), e(t["lede"]), "bench"), shell.header(lang, "bench"),
        '<main id="main" class="bench">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p><p>{link("methodology.html", t["method"])}</p>{preview_note}'),
        shell.toc(lang, [("open", e(t["open"]), None), ("closed", e(t["closed"]), None)]),
        f'<section id="open" class="wrap domain"><h2>{e(t["open"])}</h2><p class="sub">{e(t["open_text"])}</p>',
        category_table(t, open_link, preview=data is None), open_panel, "</section>\n",
        f'<section id="closed" class="wrap domain"><details class="method"><summary>{e(t["closed"])}</summary><p>{e(t["closed_text"])}</p>',
        category_table(t, missing=t["closed_missing"], preview=data is None), "</details></section>\n",
        '</main>\n', shell.footer(['<p><a href="./">HeOCR</a></p>']), shell.tail(lang),
    ])


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
    stale = []
    for lang in shell.LANGS:
        for key, output in (("bench", page(lang, data, args.public_pages)), ("methodology", build_methodology.page(lang))):
            relative = shell.site_path(lang, key)
            path = output_dir / relative
            if args.check:
                if not path.is_file() or path.read_text(encoding="utf-8") != output:
                    stale.append(relative)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output, encoding="utf-8")
    if stale:
        print("out of date: " + ", ".join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
