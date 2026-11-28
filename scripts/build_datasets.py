"""Build the dataset catalog page (datasets.html, en/datasets.html) and the home page's summary of it,
from pinned release metadata.

Site review 2, ARCH-01: the full catalog moved from the home page to its own page; home keeps the totals,
one card per group and a link to the catalog.
"""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "datasets" / "catalog.json"
# htext's line counts, one rule for both pages (site review 2, FIX-03; htext #87 writes it): for an htext
# repository listed there, its "lines" replace the catalog's.
HTEXT_COUNTS = ROOT / "htext" / "line_counts.json"
HOME = {"he": ROOT / "index.html", "en": ROOT / "en" / "index.html"}
PAGE = {"he": ROOT / "datasets.html", "en": ROOT / "en" / "datasets.html"}
SECTION = re.compile(r'^  <section id="datasets"[^>]*>.*?^  </section>', re.M | re.S)
GROUPS = {
    "real": {"en": "Real image data", "he": "תמונות ממסמכים אמיתיים"},
    "text": {"en": "Text corpora", "he": "מאגרי טקסט"},
    "synthetic": {"en": "Synthetic and mixed training data", "he": "נתוני אימון סינתטיים ומשולבים"},
    "benchmarks": {"en": "Benchmarks", "he": "מאגרי הערכה"},
}
COPY = {
    "en": {
        "title": "Datasets",
        "source": "Catalog as of {date}. Rights and permitted uses are stated with each release.",
        "coverage": "The dataset count includes superseded releases and collections. The content totals count current source releases once, with possible overlap between sources. Reported source pages include separately counted subsets.",
        "stats": {"datasets": "datasets", "documents": "documents or works", "pages": "source pages",
                  "images": "images", "lines": "lines", "words": "words", "characters": "characters", "bytes": "bytes"},
        "one_document": "document or work",
        "approval": "Access requires approval",
        "current": "Current release",
        "superseded": "Superseded (kept for reproducibility)",
        "withdrawn": "Withdrawn",
        "pending": "Publication pending",
        "versions": "Versions",
        "experimental": "EXPERIMENTAL",
        "synthetic_note": "A gain attributable to synthetic data over the best open models on real held-out sets remains unverified. Our strongest results use training mixes that include real line images and their transcriptions.",
        "by_source": {"real": "Real image datasets by source", "text": "Text corpora by source"},
        "legacy": "Also on GitHub",
        "hash": "Archive of scanned Hebrew handwriting",
        "glyphs": "Cropped Hebrew handwriting glyphs",
        "desc": "HeOCR's open datasets for Hebrew OCR: real document images, text corpora, synthetic training data and benchmarks, each with its rights.",
        "group_count": "{n} datasets",
        "full": "The full catalog",
    },
    "he": {
        "title": "מאגרי נתונים",
        "source": "הקטלוג נכון ל־{date}. זכויות ותנאי שימוש מופיעים ליד כל גרסה.",
        "coverage": "מספר המאגרים כולל גם גרסאות שהוחלפו ואוספים מאוחדים. סכומי התוכן סופרים כל גרסת מקור עדכנית פעם אחת, וייתכן שיש חפיפה בין המקורות. ספירת עמודי המקור כוללת גם נתונים שדווחו רק לחלק ממאגר.",
        "stats": {"datasets": "מאגרים", "documents": "מסמכים או יצירות", "pages": "עמודי מקור",
                  "images": "תמונות", "lines": "שורות", "words": "מילים", "characters": "תווים", "bytes": "בתים"},
        "one_document": "מסמך או יצירה",
        "approval": "הגישה דורשת אישור",
        "current": "הגרסה העדכנית",
        "superseded": "גרסה שהוחלפה (נשמרת לצורך שחזור)",
        "withdrawn": "הוסרה",
        "pending": "טרם פורסם",
        "versions": "גרסאות",
        "experimental": "ניסיוני",
        "synthetic_note": "במבחנים על מסמכים אמיתיים שהופרדו מהאימון, טרם מדדנו שיפור שניתן לייחס לנתונים סינתטיים מעבר לביצועי המודלים הפתוחים המובילים. התוצאות הטובות ביותר שלנו התקבלו באימון שכלל תמונות של שורות אמיתיות ואת התמלול שלהן.",
        "by_source": {"real": "מאגרי תמונות לפי מקור", "text": "מאגרי טקסט לפי מקור"},
        "legacy": "מאגרים נוספים ב־GitHub",
        "hash": "ארכיון סריקות של כתבי יד בעברית",
        "glyphs": "חיתוכי אותיות עבריות בכתב יד",
        "desc": "מאגרי הנתונים הפתוחים של HeOCR לזיהוי טקסט עברי: תמונות ממסמכים אמיתיים, מאגרי טקסט, נתוני אימון סינתטיים ומאגרי הערכה, כל אחד עם הזכויות שלו.",
        "group_count": "{n} מאגרים",
        "full": "לקטלוג המלא",
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
HUB_ID = re.compile(r"HeOCR/[a-z0-9-]+")


def load_catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = data["datasets"]
    htext = json.loads(HTEXT_COUNTS.read_text(encoding="utf-8"))["repositories"]
    for row in entries:
        if row["id"] in htext:
            row["counts"]["lines"] = htext[row["id"]]["lines"]
    if missing := set(htext) - {row["id"] for row in entries}:
        raise ValueError(f"htext line counts for repositories not in the catalog: {sorted(missing)}")
    model = data["model"]
    versions = [model, {**model, **model["previous"]}]
    if len({row["id"] for row in entries}) != len(entries):
        raise ValueError("Dataset ids must be unique")
    if any(not re.fullmatch(r"v[0-9]+\.[0-9]+", row["version"]) for row in versions):
        raise ValueError("Expected exact public model version tags")
    for row in [*entries, *versions]:
        if not HUB_ID.fullmatch(row["id"]) or not re.fullmatch(r"[0-9a-f]{40}", row["revision"]):
            raise ValueError("Expected exact public Hub pins")
        if any(not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", d["id"]) for d in row["dois"]):
            raise ValueError(f"Unexpected DOI for {row['id']}")
    for row in entries:
        if row["group"] not in GROUPS or row["license"] not in LICENSES:
            raise ValueError(f"Unknown catalog group or licence for {row['id']}")
        if row.get("status") not in (None, "current", "superseded"):
            raise ValueError(f"Unexpected release status for {row['id']}")
        if type(row.get("duplicates_sources", False)) is not bool:
            raise ValueError(f"Expected a boolean duplicates_sources for {row['id']}")
        if (path := row.get("release_path")) and not re.fullmatch(r"[a-z0-9.-]+(?:/[a-z0-9.-]+)*", path):
            raise ValueError(f"Invalid release path for {row['id']}")
        for value in [*row["counts"].values(), *row.get("release_counts", {}).values()]:
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"Counts must be nonnegative integers for {row['id']}")
        partial = row["partial_pages"]
        if partial and (row["counts"]["pages"] is not None or type(partial["count"]) is not int or partial["count"] < 0):
            raise ValueError(f"Partial page counts must complement missing full counts for {row['id']}")
    by_id = {row["id"]: row for row in entries}
    for row in entries:
        if family_id := row.get("family"):
            family = by_id.get(family_id)
            if not family or family.get("family") or family["group"] != row["group"]:
                raise ValueError(f"Invalid family for {row['id']}")
        for previous in row.get("hub_versions", []):
            if not re.fullmatch(r"[0-9a-f]{40}", previous["revision"]):
                raise ValueError(f"Expected pinned version of {row['id']}")
    for group, slots in data["collections"].items():
        if group not in COPY["en"]["by_source"]:
            raise ValueError(f"Unknown collection group: {group}")
        if len({slot["id"] for slot in slots}) != len(slots):
            raise ValueError(f"Collection slots must be unique for {group}")
        for slot in slots:
            if not HUB_ID.fullmatch(slot["id"]) or slot["license"] not in LICENSES:
                raise ValueError(f"Invalid collection slot: {slot}")
            row = by_id.get(slot["id"])
            if row and (row["group"] != group or row["license"] != slot["license"]):
                raise ValueError(f"Collection slot disagrees with release: {slot['id']}")
    for group, components in data["source_components"].items():
        if group not in data["collections"]:
            raise ValueError(f"Unknown source disclosure: {group}")
        for component in components:
            if component["id"] not in by_id or not re.fullmatch(
                r"[a-z0-9-]+(?:/[a-z0-9-]+)*", component["path"]
            ):
                raise ValueError(f"Invalid source component: {component}")
    return data


def number(value: int) -> str:
    return f'<bdi dir="ltr">{value:,}</bdi>'


def size(value: int, unit_name: str) -> str:
    """A byte count for people (decimal units, as HF shows them), the exact count in the tooltip
    (site review 2, FIX-01)."""
    shown, unit = float(value), "B"
    for unit in ("B", "kB", "MB", "GB", "TB"):
        if shown < 1000 or unit == "TB":
            break
        shown /= 1000
    text = f"{value:,} B" if unit == "B" else f"{shown:.2f} {unit}"
    return f'<bdi dir="ltr" title="{value:,} {unit_name}">{text}</bdi>'


def statistic(key: str, value: int, lang: str) -> str:
    t = COPY[lang]
    if key == "bytes":
        return size(value, escape(t["stats"]["bytes"]))
    name = escape(t["one_document"] if key == "documents" and value == 1 else t["stats"][key])
    return f"{number(value)} {name}"


def sum_reported(entries: list[dict], key: str) -> int | None:
    counts = [row["counts"][key] for row in entries if row["counts"][key] is not None]
    if key == "pages":
        counts.extend(row["partial_pages"]["count"] for row in entries if row["partial_pages"])
    return sum(counts) if counts else None


def release_links(row: dict, *, model: bool = False, latest_only: bool = False) -> str:
    kind = "" if model else "datasets/"
    root = f"https://huggingface.co/{kind}{escape(row['id'], quote=True)}"
    revision = row["version"] if model else row["revision"]
    url = root if row.get("access") == "manual" else f"{root}/tree/{revision}"
    if row.get("release_path") and row.get("access") != "manual":
        url += f'/{escape(row["release_path"], quote=True)}'
    links = [f'<a href="{url}">Hugging Face</a>']
    dois = row["dois"][-1:] if latest_only else row["dois"]
    for ref in dois:
        label = "Zenodo" if len(dois) == 1 else f"Zenodo {ref['label']}"
        links.append(f'<a href="https://doi.org/{ref["id"]}">{escape(label)}</a>')
    return " ".join(links)


def version_name(row: dict) -> str:
    return row.get("version") or (row["dois"][-1]["label"] if row["dois"] else "")


def version_history(row: dict, relatives: list[dict], lang: str) -> str:
    entries = []
    for sibling in relatives:
        name = escape(version_name(sibling) or sibling["title"])
        licence = escape(LICENSES[sibling["license"]][lang])
        state = f' · {escape(COPY[lang][sibling["status"]])}' if sibling.get("status") else ""
        approval = f' · {escape(COPY[lang]["approval"])}' if sibling["access"] == "manual" else ""
        stats = " · ".join(statistic(key, value, lang) for key, value in sibling["counts"].items()
                           if value is not None)
        links = release_links(sibling, latest_only=True)
        stats_html = f'<div class="catalog-licence">{stats}</div>' if stats else ""
        entries.append(f'<bdi dir="ltr">{name}</bdi> · {licence}{state}{approval} · {links}{stats_html}')
    for release in (row, *relatives):
        for previous in release.get("withdrawn_versions", []):
            entries.append(
                f'<bdi dir="ltr">{escape(previous["label"])}</bdi> · {escape(COPY[lang]["withdrawn"])}. '
                f'{escape(previous["reason"][lang])}'
            )
    for release in (*relatives, row):
        entries.extend(earlier_links(release))
    if not entries:
        return ""
    items = "".join(f'<li>{item}</li>' for item in entries)
    return (f'        <details class="versions"><summary>{escape(COPY[lang]["versions"])}</summary>'
            f'<ul>{items}</ul></details>\n')


def earlier_links(row: dict) -> list[str]:
    root = f"https://huggingface.co/datasets/{row['id']}/tree"
    by_version: dict[str, list[str]] = {}
    for previous in row.get("hub_versions", []):
        by_version.setdefault(previous["label"], []).append(
            f'<a href="{root}/{previous["revision"]}">Hugging Face</a>'
        )
    for ref in reversed(row["dois"][:-1]):
        by_version.setdefault(ref["label"], []).append(
            f'<a href="https://doi.org/{ref["id"]}">Zenodo</a>'
        )
    return [
        f'<bdi dir="ltr">{escape(label)}</bdi> · {" · ".join(links)}'
        for label, links in by_version.items()
    ]


def card(row: dict, lang: str, relatives: list[dict] | None = None) -> str:
    stats = []
    for key, value in {**row["counts"], **row.get("release_counts", {})}.items():
        if key == "pages" and (partial := row["partial_pages"]):
            subset = f'<bdi dir="ltr">{escape(partial["scope"])}</bdi>'
            stats.append(statistic(key, partial["count"], lang) + f" ({subset})")
        elif value is not None:
            stats.append(statistic(key, value, lang))
    stats_html = ('        <div class="meta catalog-counts">' +
                  "".join(f"<span>{stat}</span>" for stat in stats) + "</div>\n") if stats else ""
    details = [LICENSES[row["license"]][lang]]
    if row.get("status"):
        details.append(COPY[lang][row["status"]])
    if row["access"] == "manual":
        details.append(COPY[lang]["approval"])
    edition = version_name(row)
    edition_html = f' · <bdi dir="ltr">{escape(edition)}</bdi>' if edition else ""
    return "\n".join([
        '      <article class="card catalog-card">',
        f'        <h4><bdi dir="ltr">{escape(row["title"])}</bdi></h4>',
        f'        <p>{escape(row["description"][lang])}</p>',
        f'        <div class="catalog-licence">{escape(" · ".join(details))}{edition_html}</div>',
        stats_html + f'        <div class="row" dir="ltr">{release_links(row, latest_only=True)}</div>',
        version_history(row, relatives or [], lang) + '      </article>',
    ])


def family_cards(rows: list[dict], lang: str):
    relatives = {}
    for row in rows:
        if family := row.get("family"):
            relatives.setdefault(family, []).append(row)
    for row in rows:
        if not row.get("family"):
            yield card(row, lang, relatives.get(row["id"]))


def collection_section(
    rows: list[dict], slots: list[dict], components: list[tuple[str, str]], label: str, lang: str
) -> list[str]:
    by_id = {row["id"]: row for row in rows}
    lines = ['    <div class="grid">']
    for slot in slots:
        if row := by_id.pop(slot["id"], None):
            lines.append(card(row, lang))
        else:
            name = escape(slot["id"].split("/", 1)[1])
            licence = escape(LICENSES[slot["license"]][lang])
            lines.extend([
                '      <article class="card catalog-card">',
                f'        <h4><bdi dir="ltr">{name}</bdi></h4>',
                f'        <div class="catalog-licence">{licence}</div>',
                f'        <p>{escape(COPY[lang]["pending"])}</p>',
                '      </article>',
            ])
    lines.append('    </div>')
    if by_id or components:
        lines.extend([
            '    <details class="catalog-sources">',
            f'      <summary>{escape(label)}</summary>',
            '      <div class="grid">',
            *family_cards(list(by_id.values()), lang),
            '      </div>',
        ])
        if components:
            lines.extend([
                '      <ul>',
                *(f'        <li><a href="{url}">{escape(title)}</a></li>' for url, title in components),
                '      </ul>',
            ])
        lines.append('    </details>')
    return lines


def catalog(data: dict, lang: str, *, summary: bool) -> str:
    t = COPY[lang]
    entries = data["datasets"]
    by_id = {row["id"]: row for row in entries}
    current = [
        row for row in entries
        if row.get("status") != "superseded" and not row.get("duplicates_sources")
    ]
    fields = [("datasets", len(entries))] + [
        (name, sum_reported(current, name)) for name in ("images", "lines", "pages")
    ]
    totals = " · ".join(statistic(name, count, lang) for name, count in fields if count is not None)
    date = f'<bdi dir="ltr">{escape(data["as_of"])}</bdi>'
    head = [
        f'    <p class="sub">{escape(t["source"]).replace("{date}", date)}</p>',
        f'    <p class="catalog-totals"><strong>{totals}</strong></p>',
    ]
    if summary:
        cards = []
        for key, group in GROUPS.items():
            status = (f' <span class="status">{escape(t["experimental"])}</span>' if key == "synthetic" else "")
            count = sum(1 for row in entries if row["group"] == key)
            cards.extend([
                '      <div class="card">',
                f'        <h3><a href="datasets.html#{key}">{escape(group[lang])}</a>{status}</h3>',
                f'        <p>{escape(t["group_count"]).replace("{n}", number(count))}</p>',
                '      </div>',
            ])
        return "\n".join([
            '  <section id="datasets">', f'    <h2>{escape(t["title"])}</h2>', *head,
            '    <div class="grid">', *cards, '    </div>',
            f'    <p><a href="datasets.html">{escape(t["full"])}</a></p>', '  </section>',
        ])
    lines = ['  <section id="datasets">', *head, f'    <p class="sub">{escape(t["coverage"])}</p>']
    for key, group in GROUPS.items():
        title = escape(group[lang])
        if key == "synthetic":
            lines.append(f'    <h3 id="{key}">{title} <span class="status">{escape(t["experimental"])}</span></h3>')
            lines.append(f'    <p class="sub">{escape(t["synthetic_note"])}</p>')
        else:
            lines.append(f'    <h3 id="{key}">{title}</h3>')
        rows = [row for row in entries if row["group"] == key]
        if slots := data["collections"].get(key):
            components = [
                (
                    f"https://huggingface.co/datasets/{part['id']}/tree/{by_id[part['id']]['revision']}/{part['path']}",
                    part["title"][lang],
                )
                for part in data["source_components"].get(key, [])
            ]
            lines.extend(collection_section(rows, slots, components, t["by_source"][key], lang))
        else:
            lines.extend(['    <div class="grid">', *family_cards(rows, lang), '    </div>'])
    lines.extend([
        f'    <h3>{escape(t["legacy"])}</h3>',
        '    <ul>',
        f'      <li><a href="https://github.com/HeOCR/hash">HASH</a> · {escape(t["hash"])}</li>',
        f'      <li><a href="https://github.com/HeOCR/hletterscript">hletterscript</a> · {escape(t["glyphs"])}</li>',
        '    </ul>',
        '  </section>',
    ])
    return "\n".join(lines)


def render(data: dict, lang: str, text: str) -> str:
    """The home page with its dataset summary refreshed."""
    new, replaced = SECTION.subn(lambda _: catalog(data, lang, summary=True), text)
    if replaced != 1:
        raise ValueError(f"Expected one existing dataset section for {lang}")
    return new


def page(data: dict, lang: str) -> str:
    """datasets.html: the full catalog on the site shell."""
    t = COPY[lang]
    return "".join([
        shell.head(lang, escape(t["title"]), escape(t["desc"]), "datasets"),
        shell.header(lang, "datasets"),
        shell.page_head(escape(t["title"]), f'<p class="lede">{escape(t["desc"])}</p>'),
        '<main id="main" class="wrap home">\n',
        catalog(data, lang, summary=False), "\n",
        "</main>\n",
        shell.footer(['<p><a href="rights.html">' + shell.STR[lang]["nav"]["rights"] + '</a> · <a href="./">HeOCR</a></p>'], lang),
        shell.tail(lang),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load_catalog()
    stale = []
    outputs = [(path, render(data, language, path.read_text(encoding="utf-8"))) for language, path in HOME.items()]
    outputs += [(path, page(data, language)) for language, path in PAGE.items()]
    for path, expected in outputs:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if expected != current:
            if args.check:
                stale.append(str(path.relative_to(ROOT)))
            else:
                path.write_text(expected, encoding="utf-8")
    if stale:
        raise SystemExit("Stale dataset pages: " + ", ".join(stale))


if __name__ == "__main__":
    main()
