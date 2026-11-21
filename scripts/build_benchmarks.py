"""Build the placeholder benchmark pages; no result is displayed before review."""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
e = html.escape
T = {
    "en": {
        "title": "HeOCR benchmarks", "lede": "Real-world held-out benchmarks, with open sets first.",
        "open": "Open held-out sets", "open_text": "The headline results will use publishable images and references from multiple sources, so others can reproduce them.",
        "closed": "Closed held-out sets", "closed_text": "Closed sets may include private sources. They will also be reported, but cannot be independently reproduced in full.",
        "category": "Category", "result": "Held-out result", "missing": "Not measured on a held-out set yet",
        "categories": ["Modern printed, unpointed", "Modern printed, pointed", "Modern handwriting", "Historical printed, unpointed", "Historical printed, pointed", "Historical handwriting"],
        "method": "Read the benchmark methodology", "note": "Results and comparisons will be added after eligible held-out scoring and review.",
    },
    "he": {
        "title": "מדדי ביצועים של HeOCR", "lede": "מבחנים על נתונים אמיתיים שהוחזקו בצד, עם הקבוצות הפתוחות תחילה.",
        "open": "קבוצות פתוחות שהוחזקו בצד", "open_text": "התוצאות המרכזיות יתבססו על תמונות וטקסטי ייחוס שניתן לפרסם, ממקורות רבים, כדי שאחרים יוכלו לשחזר אותן.",
        "closed": "קבוצות סגורות שהוחזקו בצד", "closed_text": "קבוצות סגורות עשויות לכלול מקורות פרטיים. גם תוצאותיהן ידווחו, אך לא ניתן לשחזר אותן במלואן באופן עצמאי.",
        "category": "קטגוריה", "result": "תוצאה על קבוצה מוחזקת בצד", "missing": "עוד לא נמדד על קבוצה מוחזקת בצד",
        "categories": ["דפוס מודרני ללא ניקוד", "דפוס מודרני מנוקד", "כתב יד מודרני", "דפוס היסטורי ללא ניקוד", "דפוס היסטורי מנוקד", "כתב יד היסטורי"],
        "method": "לשיטת בניית המבחנים", "note": "תוצאות והשוואות יתווספו לאחר הערכה על קבוצות מתאימות שהוחזקו בצד ובדיקתן.",
    },
}


def table(t):
    rows = "".join(f'<tr><th scope="row">{e(name)}</th><td>{e(t["missing"])}</td></tr>\n' for name in t["categories"])
    return (f'<div class="tablewrap"><table><thead><tr><th scope="col">{e(t["category"])}</th>'
            f'<th scope="col">{e(t["result"])}</th></tr></thead><tbody>{rows}</tbody></table></div>\n')


def page(lang):
    t = T[lang]
    return "".join([
        shell.head(lang, e(t["title"]), e(t["lede"]), "bench"), shell.header(lang, "bench"),
        '<main id="main" class="bench">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p><p><a href="methodology.html">{e(t["method"])}</a></p>'),
        shell.toc(lang, [("open", e(t["open"]), None), ("closed", e(t["closed"]), None)]),
        f'<section id="open" class="wrap domain"><h2>{e(t["open"])}</h2><p class="sub">{e(t["open_text"])}</p>{table(t)}</section>\n',
        f'<section id="closed" class="wrap domain"><details class="method"><summary>{e(t["closed"])}</summary><p>{e(t["closed_text"])}</p>{table(t)}</details></section>\n',
        f'<p class="wrap note">{e(t["note"])}</p></main>\n', shell.footer(['<p><a href="./">HeOCR</a></p>']), shell.tail(lang),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for lang, path in (("he", ROOT / "benchmarks.html"), ("en", ROOT / "en/benchmarks.html")):
        output = page(lang)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != output:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(output, encoding="utf-8")
    if stale:
        print("out of date: " + ", ".join(stale), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
