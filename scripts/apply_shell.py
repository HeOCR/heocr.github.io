"""Keep the shared shell of the hand-written pages in sync with scripts/shell.py.

    python3 scripts/apply_shell.py           # rewrite the shell blocks of index.html, rights.html (HE at the root, EN under en/)
    python3 scripts/apply_shell.py --check   # exit 1 if a page's shell differs from shell.py

The hand-written pages carry three marked blocks, which this script owns:

    <!-- shell:head -->    … fonts, site.css, theme script, icons, link previews …   <!-- /shell:head -->
    <!-- shell:header -->  … skip link and site header …                              <!-- /shell:header -->
    <!-- shell:tail -->    … theme.js …                                               <!-- /shell:tail -->

The home pages also take their release status and introduction from this builder.
The generated pages (benchmarks, htext) get the same blocks from their build scripts.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402
from build_datasets import LICENSES, load_catalog  # noqa: E402
from build_download import COMPASS, FAMILIES, T as DOWNLOAD  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HAND = {"home": "index.html", "rights": "rights.html"}
HOME = {
    "en": {
        "intro": "Open data and tools for reading Hebrew documents, both printed and handwritten. Every dataset item has its own rights record.",
        "models": "Models and pipeline",
        "status": "Four HeOCR OCR models for Tesseract 5, one for each kind of printed document.",
        "model_link": "Get the OCR weights",
        "download": "Download",
        "sources": "The releases use public-domain or openly licensed sources. Each item keeps its source and credit.",
        "wikisource": "Hebrew Wikisource text appears in the training corpora and in line pairs. Releases link to source revisions and record the CC BY-SA terms.",
    },
    "he": {
        "intro": "נתונים וכלים פתוחים לקריאת מסמכים בעברית, מודפסים וכתובים ביד. לכל פריט במאגרי הנתונים יש רשומת זכויות משלו.",
        "models": "מודלים וצינור העיבוד",
        "status": "ארבעה מודלים של HeOCR לזיהוי תווים עם Tesseract 5, אחד לכל סוג של מסמך מודפס.",
        "model_link": "הורדת משקלי המודל",
        "download": "הורדה",
        "sources": "הגרסאות משתמשות במקורות בנחלת הכלל או ברישיון פתוח. כל פריט שומר את המקור ואת הקרדיט שלו.",
        "wikisource": "טקסט מוויקיטקסט העברית מופיע במאגרי האימון ובזוגות השורות. בכל גרסה יש קישורים למקורות ותיעוד של תנאי CC BY-SA.",
    },
}


def home_status(lang: str, text: str) -> str:
    t = HOME[lang]
    model = load_catalog()["model"]
    model_licence = html.escape(LICENSES[model["license"]][lang])
    # The same four models, in the same order, as the download page's choice compass (COPY-05).
    d = DOWNLOAD[lang]
    model_links = "".join(
        f'      <li><strong>{html.escape(d[use])}:</strong> <a href="download.html#{anchor}">'
        f'<bdi dir="ltr">{html.escape(title)} {html.escape(version)}</bdi></a> · '
        f'<a href="{hub}/tree/{version}">Hugging Face</a> <a href="https://doi.org/{doi}">Zenodo</a></li>\n'
        for (anchor, use, _), (title, version, _, _, hub, doi, *_) in zip(COMPASS, FAMILIES)
    )
    intro = html.escape(t["intro"])
    text = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{intro}">', text, count=1)
    text = re.sub(r'<p class="lede">.*?</p>', f'<p class="lede">{intro}</p>', text, count=1, flags=re.S)
    text = re.sub(
        r'(<a class="btn" href="download.html">)[^<]*(</a>)',
        lambda match: match[1] + html.escape(t["download"]) + match[2],
        text,
        count=1,
    )
    text = re.sub(
        r'^  <section id="models">.*?^  </section>',
        lambda _: (
            '  <section id="models">\n'
            f'    <h2>{html.escape(t["models"])}</h2>\n'
            f'    <p class="sub">{html.escape(t["status"])}</p>\n'
            f'    <p><a href="download.html#models">{html.escape(t["model_link"])}</a></p>\n'
            f'    <div class="meta"><span>{model_licence}</span></div>\n'
            f'    <ul>\n{model_links}    </ul>\n'
            '  </section>'
        ),
        text,
        count=1,
        flags=re.M | re.S,
    )
    text = re.sub(
        r'(<section id="sources">\s*<h2>[^<]+</h2>\s*<p class="sub">).*?( <a href="rights.html">.*?</p>)',
        lambda m: m[1] + html.escape(t["sources"]) + m[2],
        text,
        count=1,
    )
    return re.sub(
        r'(<h3><a href="https://he.wikisource.org">[^<]+</a></h3>\s*<p>).*?(</p>)',
        lambda m: m[1] + html.escape(t["wikisource"]) + m[2],
        text,
        count=1,
    )


def block(name: str, body: str) -> str:
    return f"<!-- shell:{name} -->\n{body.rstrip()}\n<!-- /shell:{name} -->"


def render(page: str, lang: str, text: str) -> str:
    if page == "home":
        text = home_status(lang, text)
    title = re.search(r"<title>(.*?)</title>", text, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)">', text)
    desc = desc.group(1) if desc else None
    parts = {
        "head": shell.head_assets(lang, title, desc, page),
        "header": shell.header(lang, page),
        "tail": f'<script src="{shell.prefix(lang)}theme.js"></script>',
    }
    for name, body in parts.items():
        pattern = re.compile(rf"<!-- shell:{name} -->.*?<!-- /shell:{name} -->", re.S)
        if not pattern.search(text):
            raise SystemExit(f"{page}/{lang}: no <!-- shell:{name} --> block")
        text = pattern.sub(lambda _m: block(name, body), text, count=1)
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for page in HAND:
        for lang in shell.LANGS:
            rel = shell.site_path(lang, page)
            path = ROOT / rel
            old = path.read_text(encoding="utf-8")
            new = render(page, lang, old)
            if a.check:
                if new != old:
                    stale.append(rel)
            elif new != old:
                path.write_text(new, encoding="utf-8")
    if stale:
        print("shell out of date:", ", ".join(stale), "— run python3 scripts/apply_shell.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
