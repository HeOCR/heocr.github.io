"""Build bilingual benchmark release pages in a local staging directory."""
from __future__ import annotations

import argparse
import html
import sys
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
        "open_result": "P-mod-open v0 results", "closed_result": "UC-W aggregates", "dataset": "Download the benchmark dataset",
        "pages": "{pages} registered pages", "published": "The public dataset includes {public} of the {registered} scored pages. The figures use the registered scope.",
        "closed_pages": "{pages} pages. Aggregate results only.",
        "reader": "Reader", "cer": "Character error rate", "wer": "Word error rate", "interval": "95% confidence interval",
        "lower": "Lower error rates are better. The tables show 95% confidence intervals where available.",
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
        "open_result": "תוצאות P-mod-open v0", "closed_result": "תוצאות מצרפיות של UC-W", "dataset": "להורדת מערך המבחן",
        "pages": "{pages} עמודים רשומים", "published": "מערך הנתונים הציבורי כולל {public} מתוך {registered} העמודים שהוערכו. התוצאות מחושבות לפי הקבוצה הרשומה.",
        "closed_pages": "{pages} עמודים. מוצגות תוצאות מצרפיות בלבד.",
        "reader": "מנוע זיהוי", "cer": "שיעור שגיאות תווים", "wer": "שיעור שגיאות מילים", "interval": "רווח סמך של 95%",
        "lower": "שיעור שגיאות נמוך יותר עדיף. רווחי סמך של 95% מוצגים כשיש כאלה.",
    },
}


def category_table(t, scored_link="", preview=False):
    rows = []
    for index, name in enumerate(t["categories"]):
        missing = "—" if preview else e(t["missing"])
        result = scored_link if index == 0 and scored_link else missing
        rows.append(f'<tr><th scope="row">{e(name)}</th><td>{result}</td></tr>\n')
    return (
        f'<div class="tablewrap"><table><thead><tr><th scope="col">{e(t["category"])}</th>'
        f'<th scope="col">{e(t["result"])}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>\n'
    )


def metric_cell(t, metric):
    if metric is None or metric["percent"] is None:
        return '<td class="num">—</td>'
    value = f'<bdi dir="ltr">{metric["percent"]}%</bdi>'
    interval = ""
    if metric["ci95"] is not None:
        lo, hi = metric["ci95"]
        interval = f'<span class="ci" title="{e(t["interval"])}"><bdi dir="ltr">{lo}–{hi}%</bdi></span>'
    denominator = ""
    if metric["denominator"] is not None:
        denominator = f'<span class="tag-n block"><bdi dir="ltr">n = {metric["denominator"]:,}</bdi></span>'
    return f'<td class="num"><span class="v">{value}</span>{interval}{denominator}</td>'


def result_table(t, caption, results, heading_level):
    metrics = [m for m in ("cer", "wer") if any(m in row["metrics"] for row in results)]
    columns = "".join(f'<th scope="col">{e(t[m])}</th>' for m in metrics)
    rows = []
    for row in results:
        cells = "".join(metric_cell(t, row["metrics"].get(m)) for m in metrics)
        rows.append(f'<tr><th scope="row"><bdi>{e(row["reader"])}</bdi></th>{cells}</tr>')
    return (
        f'<h{heading_level} id="{caption[0]}">{e(caption[1])}</h{heading_level}>'
        f'<div class="tablewrap narrow" role="region" tabindex="0" aria-labelledby="{caption[0]}">'
        f'<table><thead><tr><th scope="col">{e(t["reader"])}</th>{columns}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>\n'
    )


def link(target, label):
    return f'<a href="{target}">{e(label)}</a>'


def open_results(lang, data):
    t = T[lang]
    out = [
        f'<h3 id="p-mod-open">{e(t["open_result"])}</h3>',
        f'<p>{e(t["pages"].format(pages=31))} · {link(DATASET, t["dataset"])}</p>',
    ]
    if data["public_pages"] != 31:
        out.append(f'<p class="note">{e(t["published"].format(public=data["public_pages"], registered=31))}</p>')
    out.append(f'<p class="note">{e(t["lower"])}</p>')
    for i, view in enumerate(data["views"], start=1):
        heading = f"p-mod-open-view-{i}"
        out.append(f'<section aria-labelledby="{heading}"><h4 id="{heading}">{e(view["name"][lang])}</h4>')
        for carrier_id, names in data["carriers"].items():
            out.append(result_table(t, (f"{heading}-{carrier_id}", names[lang]), view["results"][carrier_id], 5))
        out.append("</section>")
    return "".join(out)


def closed_results(t, data):
    return (
        f'<section id="uc-w"><p>{e(t["closed_pages"].format(pages=data["pages"]))}</p>'
        + result_table(t, ("uc-w-results", t["closed_result"]), data["results"], 3)
        + "</section>"
    )


def page(lang, data):
    t = T[lang]
    open_link = link("#p-mod-open", t["open_result"]) if data is not None else ""
    closed_link = link("#uc-w", t["closed_result"]) if data is not None else ""
    open_panel = open_results(lang, data["p_mod_open"]) if data is not None else ""
    closed_panel = closed_results(t, data["uc_w"]) if data is not None else ""
    preview_note = f'<p class="note">{e(t["preview"])}</p>' if data is None else ""
    return "".join([
        shell.head(lang, e(t["title"]), e(t["lede"]), "bench"), shell.header(lang, "bench"),
        '<main id="main" class="bench">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p><p>{link("methodology.html", t["method"])}</p>{preview_note}'),
        shell.toc(lang, [("open", e(t["open"]), None), ("closed", e(t["closed"]), None)]),
        f'<section id="open" class="wrap domain"><h2>{e(t["open"])}</h2><p class="sub">{e(t["open_text"])}</p>',
        category_table(t, open_link, preview=data is None), open_panel, "</section>\n",
        f'<section id="closed" class="wrap domain"><details class="method"><summary>{e(t["closed"])}</summary><p>{e(t["closed_text"])}</p>',
        category_table(t, closed_link, preview=data is None), closed_panel, "</details></section>\n",
        '</main>\n', shell.footer(['<p><a href="./">HeOCR</a></p>']), shell.tail(lang),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--release-data", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if (args.release_data is None) != (args.sha256 is None):
        parser.error("--release-data and --sha256 must be provided together")
    output_dir = args.out_dir.resolve()
    if output_dir.is_relative_to(ROOT):
        parser.error("--out-dir must be outside this site checkout")
    try:
        data = benchmark_release_data.load(args.release_data, args.sha256) if args.release_data else None
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    stale = []
    for lang in shell.LANGS:
        for key, output in (("bench", page(lang, data)), ("methodology", build_methodology.page(lang))):
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
