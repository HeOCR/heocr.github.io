"""Generate the bilingual public leaderboard from external results.json."""

import argparse
from hashlib import sha256
from html import escape as e
import json
from pathlib import Path

import shell
from leaderboard_results import CATEGORIES, DATASET, READER_TYPES, RESULTS_REPO, STRATA, VIEWS, percentage, ranked, validate

SITE = Path(__file__).resolve().parents[1]
SPACE = "https://huggingface.co/spaces/HeOCR/hebrew-ocr-leaderboard"
SUBMIT = "https://github.com/HeOCR/hebrew-ocr-leaderboard/blob/main/SUBMITTING.md"
HF_DATASET = f"https://huggingface.co/datasets/{DATASET}"
HF_RESULTS = f"https://huggingface.co/datasets/{RESULTS_REPO}"
COPY = {
    "he": {
        "title": "טבלת דירוג לזיהוי טקסט בעברית",
        "intro": "שיעור שגיאות תווים בעמוד במבחן הדפוס העברי שנרשם מראש. שיעור נמוך יותר עדיף.",
        "notice": "טקסטי הייחוס של גרסה v0 פורסמו עם מערך המבחן. אימון עליהם עלול לשפר את התוצאות המדווחות. בעתיד מתוכנן סט מבחן סמוי בגרסה v1.",
        "results": "נתוני התוצאות", "dataset": "מערך המבחן", "submit": "הגשת תוצאות דרך GitHub", "space": "טבלת דירוג ב־Hugging Face",
        "coming": "בקרוב", "view": "תצוגת ציונים", "verified": "כן", "unverified": "לא",
        "columns": ("מנוע זיהוי", "גרסה", "סוג", "רישיון"), "trailing": ("תאריך", "גרסת המעריך", "אומת"),
        "scope": "{pages} עמודים · {carriers} גרסאות מקור",
    },
    "en": {
        "title": "Hebrew OCR leaderboard",
        "intro": "Page character error rate on the registered Hebrew print benchmark. Lower is better.",
        "notice": "P-mod-open v0 has public reference texts, so training on them can inflate scores. A hidden v1 split is planned.",
        "results": "Results data", "dataset": "Benchmark dataset", "submit": "Submit via GitHub", "space": "Leaderboard on Hugging Face",
        "coming": "Coming", "view": "Score view", "verified": "Yes", "unverified": "No",
        "columns": ("Reader", "Version", "Type", "Licence"), "trailing": ("Date", "Scorer version", "Verified"),
        "scope": "{pages} pages · {carriers} carriers",
    },
}


def table(data, view, lang):
    t = COPY[lang]
    index = int(lang == "he")
    columns = (*t["columns"], *(s[index] for s in STRATA.values()), *t["trailing"])
    headings = "".join(f'<th scope="col">{e(heading)}</th>' for heading in columns)
    rows = []
    for row in ranked(data, view):
        category = READER_TYPES[row["type"]] if lang == "he" else row["type"]
        status = t["verified"] if row["verified"] else t["unverified"]
        metrics = [percentage(row["views"][view][key]) for key in STRATA]
        cells = (row["version"], category, row["licence"], *metrics, row["date"], row["scorer_version"], status)
        scores = "".join(f"<td><bdi>{e(value)}</bdi></td>" for value in cells)
        rows.append(f'<tr><th scope="row"><bdi>{e(row["reader"])}</bdi></th>{scores}</tr>\n')
    caption = e(VIEWS[view][index])
    return (
        f'<h3 id="board-{view}">{caption}</h3><div class="tablewrap" role="region" tabindex="0" '
        f'aria-labelledby="board-{view}"><table><thead><tr>{headings}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def page(lang, data):
    t = COPY[lang]
    index = int(lang == "he")
    scope = e(t["scope"].format(**data["benchmark"]))
    links = " · ".join(f'<a href="{url}">{e(t[key])}</a>' for key, url in (
        ("dataset", HF_DATASET), ("results", HF_RESULTS), ("space", SPACE), ("submit", SUBMIT),
    ))
    intro = f'<p class="lede">{e(t["intro"])}</p><p>{links}</p><p class="note">{e(t["notice"])}</p>'
    categories = [(key, f"<bdi>{key}</bdi> · {e(label[index])}", e(t["coming"]) if key != "C1" else None)
                  for key, label in CATEGORIES.items()]
    name = categories[0][1]
    pending = "".join(
        f'<section class="wrap domain" id="{key}"><h2>{title}</h2><p>{status}</p></section>'
        for key, title, status in categories[1:]
    )
    return "".join((
        shell.head(lang, e(t["title"]), e(t["intro"]), "leaderboard"),
        shell.header(lang, "leaderboard"),
        '<main id="main" class="bench">',
        shell.page_head(e(t["title"]), intro),
        shell.toc(lang, categories),
        f'<section class="wrap domain" id="C1"><h2>{name}</h2><p>{scope}</p>',
        table(data, "filtered", lang),
        f'<details class="method"><summary>{e(VIEWS["all"][index])}</summary>',
        table(data, "all", lang),
        "</details></section>",
        pending,
        "</main>",
        shell.footer([f"<p>{links}</p>"]),
        shell.tail(lang),
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--out-dir", type=Path, default=SITE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    out = args.out_dir.resolve()
    if (args.results is None) != (args.sha256 is None):
        parser.error("--results and --sha256 must be supplied together")
    raw = (args.results or SITE / "leaderboard/results.json").read_bytes()
    if args.sha256 and sha256(raw).hexdigest() != args.sha256:
        parser.error("Results JSON does not match its SHA-256.")
    data = validate(json.loads(raw))
    for lang in shell.LANGS:
        path = out / shell.site_path(lang, "leaderboard")
        text = page(lang, data)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                parser.error(f"Stale leaderboard rendering ({lang}).")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
