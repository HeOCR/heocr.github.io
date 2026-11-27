"""Generate the English and Hebrew model downloads and app status pages."""

from __future__ import annotations

import argparse
from html import escape
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
MODEL_RELEASES = (
    ("MEASURED", "measured", "https://huggingface.co/HeOCR/heocr-p-hist-measured",
     "https://doi.org/10.5281/zenodo.24578440"),
)
T = {
    "en": {
        "title": "Download HeOCR",
        "models": "OCR models",
        "about": "Tesseract weights for historical, unpointed Hebrew print. Apache 2.0.",
        "measured": "Evaluated on the C2 held-out set. See the model card for results.",
        "apps": "Apps",
        "coming": "Coming soon",
    },
    "he": {
        "title": "הורדת HeOCR",
        "models": "מודלים לזיהוי תווים",
        "about": "משקלי Tesseract לדפוס עברי היסטורי לא מנוקד, ברישיון Apache 2.0.",
        "measured": "נבדק על מערך המבחן C2. התוצאות מופיעות בכרטיס המודל.",
        "apps": "יישומים",
        "coming": "בקרוב",
    },
}


def page(lang: str) -> str:
    text = {key: escape(value) for key, value in T[lang].items()}
    model_cards = "".join(
        f'<div class="card"><h3><bdi dir="ltr">HeOCR P-hist {variant}</bdi></h3>'
        f'<p>{text[description]}</p>'
        f'<p><a href="{escape(hf)}">Hugging Face</a> · <a href="{escape(doi)}">Zenodo</a></p></div>\n'
        for variant, description, hf, doi in MODEL_RELEASES
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
        + f'<section id="models">\n<h2>{text["models"]}</h2>\n<div class="grid">\n{model_cards}</div>\n</section>\n'
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
