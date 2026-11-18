"""Keep the shared shell of the hand-written pages in sync with scripts/shell.py.

    python3 scripts/apply_shell.py           # rewrite the shell blocks of index.html, rights.html (EN, HE)
    python3 scripts/apply_shell.py --check   # exit 1 if a page's shell differs from shell.py

The hand-written pages carry three marked blocks, which this script owns:

    <!-- shell:head -->    … fonts, site.css, theme script, icons, link previews …   <!-- /shell:head -->
    <!-- shell:header -->  … skip link and site header …                              <!-- /shell:header -->
    <!-- shell:tail -->    … theme.js …                                               <!-- /shell:tail -->

Everything else in those pages (title, description, page head, main content, footer lines) is edited by hand.
The generated pages (benchmarks, htext) get the same blocks from their build scripts.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HAND = {"home": ("index.html", "he/index.html"), "rights": ("rights.html", "he/rights.html")}


def block(name: str, body: str) -> str:
    return f"<!-- shell:{name} -->\n{body.rstrip()}\n<!-- /shell:{name} -->"


def render(page: str, lang: str, text: str) -> str:
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
    for page, paths in HAND.items():
        for lang, rel in zip(("en", "he"), paths):
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
