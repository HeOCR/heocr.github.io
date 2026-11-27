"""Generate the English and Hebrew model downloads and app status pages."""

from __future__ import annotations

import argparse
from html import escape
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
MODEL_HUB = "https://huggingface.co/HeOCR/heocr-p-hist-measured"
FULL_MODEL_HUB = "https://huggingface.co/HeOCR/heocr-p-hist-full"
QUICK_START_VERSION = "v1.1"
MODEL_RELEASES = (
    ("MEASURED", QUICK_START_VERSION, "phist-v11", "measured_latest", MODEL_HUB, "10.5281/zenodo.24581274",
     "benchmarks.html#p-hist-open-scores-filtered-pooled"),
    ("MEASURED", "v1.0", "phist-v10", "measured_previous", MODEL_HUB, "10.5281/zenodo.24578440",
     f"{MODEL_HUB}/blob/v1.0/README.md#held-out-evaluation-old-printed-hebrew-unpointed"),
    ("FULL", "v1.1-full", "phist-full-v11", "full_v11", FULL_MODEL_HUB, "10.5281/zenodo.24586339", None),
    ("FULL", "v1.0-full", "phist-full-v10", "full_v10", FULL_MODEL_HUB, "10.5281/zenodo.24582845", None),
)
QUICK_START = (
    "mkdir -p tessdata\n"
    "curl -fL -o tessdata/phist_v2.traineddata \\\n"
    f"  {MODEL_HUB}/resolve/{QUICK_START_VERSION}/phist_v2.traineddata\n"
    "tesseract page.png out -l phist_v2 --tessdata-dir ./tessdata --psm 3"
)
T = {
    "en": {
        "title": "Download HeOCR",
        "models": "OCR models",
        "about": "HeOCR P-hist v1.1 is available now for historical, unpointed Hebrew print. Apache 2.0.",
        "quick_start": "Quick start",
        "instructions": "With Tesseract 5 and curl installed, save your page as page.png and run these commands in the same directory. The result is written to out.txt.",
        "experimental": "HeOCR’s modern print and handwriting models are still experimental.",
        "modern_results": "Modern print benchmark",
        "benchmarks": "See all benchmarks",
        "model_benchmark": "C2 held-out result",
        "measured_latest": "Best / Latest. Evaluated on the C2 held-out set.",
        "measured_previous": "Previous version. Evaluated on the C2 held-out set.",
        "full_v10": "Trained with additional data. This variant is unmeasured.",
        "apps": "Apps",
        "full_v11": "Trained with additional data. This variant is unmeasured.",
        "coming": "Coming soon",
    },
    "he": {
        "title": "הורדת HeOCR",
        "models": "מודלים לזיהוי תווים",
        "about": "HeOCR P-hist v1.1 זמין להורדה לדפוס עברי היסטורי לא מנוקד, ברישיון Apache 2.0.",
        "quick_start": "התחלה מהירה",
        "instructions": "התקינו Tesseract 5 ו־curl, שמרו את העמוד בשם page.png והריצו את הפקודות מאותה תיקייה. התוצאה תישמר בקובץ out.txt.",
        "experimental": "המודלים של HeOCR לדפוס מודרני ולכתב יד עדיין ניסיוניים.",
        "modern_results": "מדד ההערכה לדפוס מודרני",
        "benchmarks": "לכל מדדי ההערכה",
        "model_benchmark": "תוצאות על מערך המבחן C2",
        "measured_latest": "הגרסה הטובה והעדכנית ביותר. נבדקה על מערך המבחן C2.",
        "measured_previous": "גרסה קודמת. נבדקה על מערך המבחן C2.",
        "full_v10": "אומן עם נתונים נוספים. גרסה זו לא נמדדה.",
        "apps": "יישומים",
        "full_v11": "אומן עם נתונים נוספים. גרסה זו לא נמדדה.",
        "coming": "בקרוב",
    },
}


def page(lang: str) -> str:
    text = {key: escape(value) for key, value in T[lang].items()}
    model_cards = []
    for variant, version, anchor, description, hub, doi, result in MODEL_RELEASES:
        benchmark = (f'<a href="{result}">{text["model_benchmark"]}</a>'
                     if result else "")
        model_cards.append(
            f'<div class="card" id="{anchor}"><h3><bdi dir="ltr">HeOCR P-hist {variant} {version}</bdi></h3>'
            f'<p>{text[description]}</p>'
            f'<div class="row"><a href="{hub}/tree/{version}">Hugging Face</a>'
            f'<a href="https://doi.org/{doi}">Zenodo</a>{benchmark}</div></div>\n'
        )
    cards = "".join(
        f'<div class="card"><h3>{platform}</h3><p>{text["coming"]}</p></div>\n'
        for platform in ("macOS", "Windows", "Android")
    )
    return (
        shell.head(lang, text["title"], text["about"], "download")
        + shell.header(lang, "download")
        + '<main id="main" class="wrap doc">\n'
        + shell.page_head(text["title"], f'<p class="lede">{text["about"]}</p>')
        + f'<section id="quick-start">\n<h2>{text["quick_start"]}</h2>\n'
          f'<p>{text["instructions"]}</p>\n'
          f'<pre class="quick-start"><code>{escape(QUICK_START)}</code></pre>\n</section>\n'
        + f'<section id="models">\n<h2>{text["models"]}</h2>\n<div class="grid">\n{"".join(model_cards)}</div>\n</section>\n'
        + f'<p>{text["experimental"]} <a href="benchmarks.html#p-mod-open">{text["modern_results"]}</a> · '
          f'<a href="benchmarks.html">{text["benchmarks"]}</a></p>\n'
        + f'<section>\n<h2>{text["apps"]}</h2>\n<div class="grid">\n{cards}</div>\n</section>\n'
        + "</main>\n"
        + shell.footer([])
        + shell.tail(lang)
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for lang, path in (("he", ROOT / "download.html"), ("en", ROOT / "en" / "download.html")):
        s = page(lang)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_download.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
