"""Generate the English and Hebrew download status pages."""

from __future__ import annotations

import argparse
from html import escape
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
T = {
    "en": {"title": "Download HeOCR", "coming": "Coming soon"},
    "he": {"title": "הורדת HeOCR", "coming": "בקרוב"},
}


def page(lang: str) -> str:
    title, coming = (escape(T[lang][key]) for key in ("title", "coming"))
    cards = "".join(
        f'<div class="card"><h3>{platform}</h3><p>{coming}</p></div>\n'
        for platform in ("macOS", "Windows", "Android")
    )
    return (
        shell.head(lang, title, coming, "download")
        + shell.header(lang, "download")
        + '<main id="main" class="wrap doc">\n'
        + shell.page_head(title, f'<p class="lede">{coming}</p>')
        + f'<div class="grid">\n{cards}</div>\n'
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
