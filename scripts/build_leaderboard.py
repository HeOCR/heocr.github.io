"""Generate the bilingual public leaderboard from external results.json."""

import argparse
from hashlib import sha256
from html import escape as e
import json
from pathlib import Path

import shell
from benchmark_release_data import PMOD_OPEN_V0_DOI_URL
from leaderboard_results import (
    CATEGORIES, DATASET, EFFICIENCY_EXECUTIONS, EFFICIENCY_PLATFORMS,
    DOCUMENT_TYPES, READER_TYPES, RESULTS_REPO, STRATA, TYPE_CAPTURES, TYPE_SCOPES, VIEWS,
    percentage, ranked, validate,
)

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
        "results": "נתוני התוצאות", "dataset": "מערך המבחן", "doi": "ציטוט מערך הנתונים (Zenodo DOI)", "submit": "הגשת תוצאות דרך GitHub", "space": "טבלת דירוג ב־Hugging Face",
        "coming": "בקרוב", "view": "תצוגת ציונים", "verified": "אומת", "unverified": "הוגש עצמאית, טרם אומת",
        "columns": ("מנוע זיהוי", "גרסה", "סוג", "רישיון"), "trailing": ("תאריך", "גרסת המעריך", "מצב אימות"),
        "how": "איך מגישים תוצאות?",
        "steps": (
            'הריצו את מנוע הזיהוי על <bdi>P-mod-open v0</bdi> והכינו קובץ <bdi>ZIP</bdi> בפורמט <bdi>heocr-bench</bdi>.',
            'פתחו בקשת מיזוג ב־<bdi>GitHub</bdi> עם קובץ התחזיות וקובץ <bdi>JSON</bdi> ובו שם המנוע, גרסה, רישיון, משקולות פתוחות או סגורות, קישור ציבורי וסכום הביקורת של הקובץ.',
            'בדקו את תגובת הניקוד ובקשו בדיקה. אפשר להגיש פעם אחת לכל צמד של מנוע וגרסה. לאחר המיזוג, התוצאה תסומן ״הוגש עצמאית, טרם אומת״ עד להרצה חוזרת של <bdi>HeOCR</bdi>.',
        ),
        "instructions": "הוראות הגשה ודוגמה",
        "scope": "{pages} עמודים · {carriers} גרסאות מקור",
    },
    "en": {
        "title": "Hebrew OCR leaderboard",
        "intro": "Page character error rate on the registered Hebrew print benchmark. Lower is better.",
        "notice": "P-mod-open v0 has public reference texts, so training on them can inflate scores. A hidden v1 split is planned.",
        "results": "Results data", "dataset": "Benchmark dataset", "doi": "Cite the dataset (Zenodo DOI)", "submit": "Submit via GitHub", "space": "Leaderboard on Hugging Face",
        "coming": "Coming", "view": "Score view", "verified": "Verified", "unverified": "Self-submitted, unverified",
        "columns": ("Reader", "Version", "Type", "Licence"), "trailing": ("Date", "Scorer version", "Status"),
        "how": "How to submit",
        "steps": (
            'Run your reader on P-mod-open v0 and package the predictions in a <bdi>heocr-bench</bdi> ZIP.',
            'Open a GitHub pull request with the ZIP and a JSON receipt listing the reader, version, licence, open or closed weights, a public link and the ZIP checksum.',
            'Read the score comment and request review. One entry per reader and version is accepted. After the lead merges it, the row is self-submitted, unverified until HeOCR reruns it.',
        ),
        "instructions": "Submission instructions and example",
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


def diagnostics(data, lang):
    labels = ("Matched originals", "Artwork-masked carriers", "Scope", "Carriers", "Filtered page CER", "All page CER")
    if lang == "he":
        labels = ("תואמים למקור", "נשאים עם מסכת סמל", "קבוצה", "נשאים", "שגיאת תווים מסוננת", "שגיאת תווים מלאה")
    sections = []
    for row in data["rows"]:
        if "diagnostic" not in row:
            continue
        details = row["diagnostic"]
        title = f'{row["reader"]} · {row["version"]} · {row["type"]}'
        parts = [
            f'<section class="method"><h3><bdi>{e(title)}</bdi></h3>',
            f'<p class="note" lang="en" dir="ltr"><strong>{e(details["notice"])}</strong></p>',
            '<div class="tablewrap"><table><thead><tr>',
            *(f'<th scope="col">{e(label)}</th>' for label in labels[2:]),
            '</tr></thead><tbody>',
        ]
        for label, count, views in (
            (labels[0], details["paired_carriers"], row["views"]),
            (labels[1], details["masked_carriers"], details["masked_views"]),
        ):
            parts.append(f'<tr><th scope="row">{e(label)}</th><td>{count}</td>'
                         f'<td>{percentage(views["filtered"]["pooled"])}</td>'
                         f'<td>{percentage(views["all"]["pooled"])}</td></tr>')
        parts.append('</tbody></table></div></section>')
        sections.append("".join(parts))
    return "".join(sections)


EFFICIENCY_COPY = {
    "en": {
        "title": "Reader efficiency",
        "note": "Each local run covers all 65 public v0 carrier images. Paddle efficiency uses ONNX CPU. Its accuracy run used CUDA. Ubuntu runner costs are projections at $0.36/hour. Gemini lists public Vertex token rates. A dash marks an unavailable value.",
        "columns": ("Reader", "Execution", "Images / runs", "Pages/min", "Peak RSS (MiB)",
                    "Marginal API USD / 1,000 pages", "Runner hours / 1,000 pages", "Runner USD / 1,000 pages",
                    "Input / output USD per 1M tokens"),
        "source": "Pinned measurements and method",
    },
    "he": {
        "title": "יעילות מנועי הזיהוי",
        "note": "כל הרצה מקומית כוללת את כל 65 התמונות הציבוריות של v0. יעילות Paddle נמדדה ב־ONNX על המעבד. הדיוק נמדד ב־CUDA. עלויות Ubuntu הן אומדן לפי 0.36 דולר לשעה. עבור Gemini מוצגים מחירי המחירון של Vertex לטוקנים. מקף מציין נתון שאינו זמין.",
        "columns": ("מנוע זיהוי", "סביבת הרצה", "תמונות / הרצות", "עמודים בדקה", "זיכרון מרבי (MiB)",
                    "עלות API שולית ל־1,000 עמודים ($)", "שעות ריצה ל־1,000 עמודים", "עלות ריצה ל־1,000 עמודים ($)",
                    "מחיר קלט / פלט למיליון טוקנים ($)"),
        "source": "מקור המדידות ושיטת המדידה",
    },
}


def efficiency(data, lang):
    panel = data.get("efficiency")
    if not panel:
        return ""
    copy = EFFICIENCY_COPY[lang]
    local = int(lang == "he")
    readers = {row["id"]: row["reader"] for row in data["rows"]}
    numbers = (
        ("pages_per_minute", ".2f"), ("peak_rss_mib", ".2f"),
        ("marginal_usd_per_1000", ".2f"), ("runner_hours_per_1000", ".3f"),
        ("runner_usd_per_1000", ".5f"),
    )
    heads = "".join(f'<th scope="col">{e(label)}</th>' for label in copy["columns"])
    parts = [f'<section class="wrap domain" id="efficiency"><h2>{e(copy["title"])}</h2><p>{e(copy["note"])}</p>']
    for platform, labels in EFFICIENCY_PLATFORMS.items():
        title_id = f"efficiency-{platform}"
        body = []
        for measure in panel["rows"]:
            if measure["platform"] != platform:
                continue
            execution = EFFICIENCY_EXECUTIONS[measure["execution"]][local + 1]
            counts = "—" if measure["pages"] is None else f'{measure["pages"]} / {measure["repetitions"]}'
            stats = [format(measure[key], fmt) if measure[key] is not None else "—" for key, fmt in numbers]
            input_rate, output_rate = measure["api_input_usd_per_million"], measure["api_output_usd_per_million"]
            rates = "—" if input_rate is None else f"{input_rate:.2f} / {output_rate:.2f}"
            cells = "".join(f"<td><bdi>{e(value)}</bdi></td>" for value in (execution, counts, *stats, rates))
            reader = readers[measure["reader_id"]]
            if measure["execution"] == "onnx-cpu":
                reader = reader.removesuffix(" (CUDA)")
            body.append(f'<tr><th scope="row"><bdi>{e(reader)}</bdi></th>{cells}</tr>')
        if body:
            parts.append(f'<h3 id="{title_id}"><bdi>{e(labels[local])}</bdi></h3>'
                         f'<div class="tablewrap" role="region" tabindex="0" aria-labelledby="{title_id}">'
                         f'<table><thead><tr>{heads}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')
    url = f'https://github.com/HeOCR/heocr-bench/tree/{panel["source_commit"]}/efficiency'
    parts.append(f'<p><a href="{url}">{e(copy["source"])}</a></p></section>')
    return "".join(parts)


TYPE_COPY = {
    "en": (
        "CER by document type and capture",
        "Gazette groups pages by source and overlaps the layout groups. Scores show CER and carrier count. "
        "Masked carriers are shown separately.",
        "Reader", "reference builder",
    ),
    "he": (
        "שיעור שגיאות תווים לפי סוג מסמך ולכידה",
        "הקבוצה ״רשומות״ כוללת עמודים לפי מקורם וחופפת לקבוצות לפי פריסה. "
        "לצד כל ציון מוצג מספר הלכידות. לכידות עם מיסוך מוצגות בנפרד.",
        "מנוע זיהוי", "השתתף בבניית הייחוס",
    ),
}


def document_types(data, lang):
    panel = data.get("document_types")
    if not panel:
        return ""
    index = int(lang == "he")
    title, note, reader_label, bias = TYPE_COPY[lang]
    columns = (reader_label, *(label[index] for label in TYPE_CAPTURES.values()))
    headings = "".join(f'<th scope="col">{e(label)}</th>' for label in columns)
    parts = [f'<section class="wrap domain" id="document-types"><h2>{e(title)}</h2><p>{e(note)}</p>']
    for scope, (count, *names) in TYPE_SCOPES.items():
        parts.append(f'<details class="method"{" open" if scope == "matched" else ""}>'
                     f'<summary>{e(names[index])} · {count}</summary>')
        for view, labels in VIEWS.items():
            parts.append(f'<details class="method"{" open" if view == "filtered" else ""}>'
                         f'<summary>{e(labels[index])}</summary>')
            for code, label in DOCUMENT_TYPES.items():
                rows = []
                for reader in panel["readers"]:
                    metrics = reader["scopes"].get(scope, {}).get(view, {}).get(code)
                    if not metrics:
                        continue
                    name = reader["reader"]
                    if reader.get("reference_builder"):
                        name += f" · {bias}"
                    cells = []
                    for cap in TYPE_CAPTURES:
                        metric = metrics.get(cap)
                        cells.append(f'{percentage(metric)} · {metric["carriers"]}' if metric else "—")
                    fields = "".join(f'<td><bdi>{e(value)}</bdi></td>' for value in cells)
                    rows.append(f'<tr><th scope="row"><bdi>{e(name)}</bdi></th>{fields}</tr>')
                if rows:
                    ident = f"type-{scope}-{view}-{code}"
                    parts.append(f'<h3 id="{ident}">{e(label[index])}</h3>'
                                 f'<div class="tablewrap" role="region" tabindex="0" aria-labelledby="{ident}">'
                                 f'<table><thead><tr>{headings}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
            parts.append("</details>")
        parts.append("</details>")
    return "".join(parts) + "</section>"


def page(lang, data):
    t = COPY[lang]
    index = int(lang == "he")
    scope = e(t["scope"].format(**data["benchmark"]))
    links = " · ".join(f'<a href="{url}">{e(t[key])}</a>' for key, url in (
        ("dataset", HF_DATASET), ("doi", PMOD_OPEN_V0_DOI_URL), ("results", HF_RESULTS), ("space", SPACE), ("submit", "#how-to-submit"),
    ))
    if data.get("efficiency"):
        links += f' · <a href="#efficiency">{e(EFFICIENCY_COPY[lang]["title"])}</a>'
    if data.get("document_types"):
        links += f' · <a href="#document-types">{e(TYPE_COPY[lang][0])}</a>'
    intro = f'<p class="lede">{e(t["intro"])}</p><p>{links}</p><p class="note">{e(t["notice"])}</p>'
    categories = [(key, f"<bdi>{key}</bdi> · {e(label[index])}", e(t["coming"]) if key != "C1" else None)
                  for key, label in CATEGORIES.items()]
    name = categories[0][1]
    pending = "".join(
        f'<section class="wrap domain" id="{key}"><h2>{title}</h2><p>{status}</p></section>'
        for key, title, status in categories[1:]
    )
    submission = "".join((
        f'<section class="wrap domain" id="how-to-submit"><h2>{e(t["how"])}</h2><ol>',
        *(f'<li>{step}</li>' for step in t["steps"]),
        f'</ol><p><a href="{SUBMIT}">{e(t["instructions"])}</a></p></section>',
    ))
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
        "</details>",
        diagnostics(data, lang),
        "</section>",
        document_types(data, lang),
        efficiency(data, lang),
        pending,
        submission,
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
