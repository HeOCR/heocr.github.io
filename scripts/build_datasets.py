"""Refresh the bilingual homepage catalog from pinned release metadata."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "datasets" / "catalog.json"
HOME = {"he": ROOT / "index.html", "en": ROOT / "en" / "index.html"}
SECTION = re.compile(r'^  <section id="datasets"[^>]*>.*?^  </section>', re.M | re.S)
GROUPS = {
    "real": {"en": "Real data", "he": "נתונים ממסמכים אמיתיים"},
    "text": {"en": "Text corpora", "he": "מאגרי טקסט"},
    "synthetic": {"en": "Synthetic training data", "he": "נתוני אימון סינתטיים"},
    "mixed": {"en": "Mixed training data", "he": "נתוני אימון משולבים"},
    "metadata": {"en": "Results and fixtures", "he": "תוצאות וקובצי בדיקה"},
}
COPY = {
    "en": {
        "title": "Datasets",
        "source": "Catalog as of {date}. Rights and permitted uses are stated with each release.",
        "coverage": "Totals add counts from the listed releases, including related releases that can overlap. Source pages include separately reported subsets. Image records include full captures and line crops.",
        "stats": {"datasets": "datasets", "documents": "documents or works", "pages": "source pages",
                  "images": "images", "lines": "lines", "words": "words", "characters": "characters", "bytes": "bytes"},
        "unknown": "not stated",
        "unknown_words": "word count not stated",
        "one_document": "document or work",
        "approval": "Access requires approval",
        "legacy": "Also on GitHub",
        "hash": "Archive of scanned Hebrew handwriting",
        "glyphs": "Cropped Hebrew handwriting glyphs",
    },
    "he": {
        "title": "מאגרי נתונים",
        "source": "הקטלוג נכון ל־{date}. זכויות ותנאי שימוש מופיעים ליד כל גרסה.",
        "coverage": "הסכומים מחברים ספירות מהגרסאות המוצגות, שעשויות לכלול פריטים חופפים. הספירה כוללת גם עמודי מקור שדווחו עבור חלק ממאגר. תמונות כוללות עמודים שלמים וחיתוכי שורות.",
        "stats": {"datasets": "מאגרים", "documents": "מסמכים או יצירות", "pages": "עמודי מקור",
                  "images": "תמונות", "lines": "שורות", "words": "מילים", "characters": "תווים", "bytes": "בתים"},
        "unknown": "לא צוין",
        "unknown_words": "מספר המילים לא צוין",
        "one_document": "מסמך או יצירה",
        "approval": "הגישה דורשת אישור",
        "legacy": "מאגרים נוספים ב־GitHub",
        "hash": "ארכיון סריקות של כתבי יד בעברית",
        "glyphs": "חיתוכי אותיות עבריות בכתב יד",
    },
}
LICENSES = {
    "cc0-1.0": {"en": "CC0 1.0", "he": "CC0 1.0"},
    "cc-by-4.0": {"en": "CC BY 4.0", "he": "CC BY 4.0"},
    "cc-by-sa-4.0": {"en": "CC BY-SA 4.0", "he": "CC BY-SA 4.0"},
    "apache-2.0": {"en": "Apache-2.0", "he": "Apache-2.0"},
    "mixed-benchmark": {"en": "CC0 for HeOCR captures and annotations. Source rights vary.",
                        "he": "תצלומי HeOCR והתיוגים ב־CC0. זכויות המקור משתנות לפי פריט."},
    "gazette": {"en": "CC0 annotations and metadata. Official source terms apply.",
                "he": "תיוגים ומטא־דאטה ב־CC0. לטקסטים הרשמיים חלים תנאי המקור."},
    "pd-cc0": {"en": "Public-domain sources. CC0 compilation and metadata.",
               "he": "מקורות בנחלת הכלל. האוסף והמטא־דאטה ב־CC0."},
    "sefaria": {"en": "Public domain or CC0 by edition.",
                "he": "נחלת הכלל או CC0, לפי מהדורה."},
}


def load_catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = data["datasets"]
    if len({row["id"] for row in entries}) != len(entries):
        raise ValueError("Dataset ids must be unique")
    for row in [*entries, data["model"]]:
        if not re.fullmatch(r"HeOCR/[a-z0-9-]+", row["id"]) or not re.fullmatch(r"[0-9a-f]{40}", row["revision"]):
            raise ValueError("Expected exact public Hub pins")
        if any(not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", d["id"]) for d in row["dois"]):
            raise ValueError(f"Unexpected DOI for {row['id']}")
    for row in entries:
        if row["group"] not in GROUPS or row["license"] not in LICENSES:
            raise ValueError(f"Unknown catalog group or licence for {row['id']}")
        for value in row["counts"].values():
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"Counts must be nonnegative integers for {row['id']}")
        partial = row["partial_pages"]
        if partial and (row["counts"]["pages"] is not None or type(partial["count"]) is not int or partial["count"] < 0):
            raise ValueError(f"Partial page counts must complement missing full counts for {row['id']}")
    return data


def number(value: int) -> str:
    return f'<bdi dir="ltr">{value:,}</bdi>'


def statistic(key: str, value: int | None, lang: str) -> str:
    t = COPY[lang]
    name = escape(t["one_document"] if key == "documents" and value == 1 else t["stats"][key])
    if value is None:
        return escape(t["unknown_words"]) if key == "words" else f"{name} · {escape(t['unknown'])}"
    return f"{number(value)} {name}"


def sum_reported(entries: list[dict], key: str) -> int | None:
    counts = [row["counts"][key] for row in entries if row["counts"][key] is not None]
    if key == "pages":
        counts.extend(row["partial_pages"]["count"] for row in entries if row["partial_pages"])
    return sum(counts) if counts else None


def release_links(row: dict, *, model: bool = False) -> str:
    kind = "" if model else "datasets/"
    root = f"https://huggingface.co/{kind}{escape(row['id'], quote=True)}"
    url = root if row.get("access") == "manual" else f"{root}/tree/{row['revision']}"
    links = [f'<a href="{url}">Hugging Face</a>']
    for ref in row["dois"]:
        label = "Zenodo" if len(row["dois"]) == 1 else f"Zenodo {ref['label']}"
        links.append(f'<a href="https://doi.org/{ref["id"]}">{escape(label)}</a>')
    return " ".join(links)


def card(row: dict, lang: str) -> str:
    stats = [statistic(key, value, lang) for key, value in row["counts"].items() if value is not None]
    if partial := row["partial_pages"]:
        subset = f'<bdi dir="ltr">{escape(partial["scope"])}</bdi>'
        stats.insert(0, statistic("pages", partial["count"], lang) + f" ({subset})")
    stats_html = "".join(f"<span>{stat}</span>" for stat in stats)
    licence = escape(LICENSES[row["license"]][lang])
    access = f' · {escape(COPY[lang]["approval"])}' if row["access"] == "manual" else ""
    return "\n".join([
        '      <article class="card catalog-card">',
        f'        <h4><bdi dir="ltr">{escape(row["title"])}</bdi></h4>',
        f'        <p>{escape(row["description"][lang])}</p>',
        f'        <div class="catalog-licence">{licence}{access}</div>',
        f'        <div class="meta catalog-counts">{stats_html}</div>',
        f'        <div class="row" dir="ltr">{release_links(row)}</div>',
        '      </article>',
    ])


def render(data: dict, lang: str, text: str) -> str:
    t = COPY[lang]
    entries = data["datasets"]
    fields = [("datasets", len(entries))] + [
        (name, sum_reported(entries, name)) for name in ("pages", "images", "lines", "words")
    ]
    totals = " · ".join(statistic(name, count, lang) for name, count in fields)
    date = f'<bdi dir="ltr">{escape(data["as_of"])}</bdi>'
    lines = [
        '  <section id="datasets">',
        f'    <h2>{escape(t["title"])}</h2>',
        f'    <p class="sub">{escape(t["source"]).replace("{date}", date)}</p>',
        f'    <p class="catalog-totals"><strong>{totals}</strong></p>',
        f'    <p class="sub">{escape(t["coverage"])}</p>',
    ]
    for key, group in GROUPS.items():
        lines.extend([f'    <h3>{escape(group[lang])}</h3>', '    <div class="grid">'])
        lines.extend(card(row, lang) for row in entries if row["group"] == key)
        lines.append('    </div>')
    lines.extend([
        f'    <h3>{escape(t["legacy"])}</h3>',
        '    <ul>',
        f'      <li><a href="https://github.com/HeOCR/hash">HASH</a> · {escape(t["hash"])}</li>',
        f'      <li><a href="https://github.com/HeOCR/hletterscript">hletterscript</a> · {escape(t["glyphs"])}</li>',
        '    </ul>',
        '  </section>',
    ])
    new, replaced = SECTION.subn(lambda _: "\n".join(lines), text)
    if replaced != 1:
        raise ValueError(f"Expected one existing dataset section for {lang}")
    return new


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load_catalog()
    stale = []
    for language, path in HOME.items():
        current = path.read_text(encoding="utf-8")
        expected = render(data, language, current)
        if expected != current:
            if args.check:
                stale.append(str(path.relative_to(ROOT)))
            else:
                path.write_text(expected, encoding="utf-8")
    if stale:
        raise SystemExit("Stale dataset sections: " + ", ".join(stale))


if __name__ == "__main__":
    main()
