"""Write the site theme (scripts/theme.py) into the hand-written pages: index.html, rights.html and their
Hebrew versions. Idempotent: a page that already carries the theme is rewritten to the same bytes.

    python3 scripts/apply_theme.py           # update the pages
    python3 scripts/apply_theme.py --check   # exit 1 if a page is out of date

It drops the automatic switch on the OS colour preference, makes the light background white, and adds
the head script, the toggle (next to the language toggle) and its click handler. The generated pages
(benchmarks, htext) take the same snippets from their build scripts.
"""
from __future__ import annotations

import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAGES = {"index.html": "en", "rights.html": "en", "he/index.html": "he", "he/rights.html": "he"}
AUTO_DARK = re.compile(r'  @media \(prefers-color-scheme: dark\) \{\n    :root:not\(\[data-theme="light"\]\) \{.*?\n    \}\n  \}\n', re.S)


def themed(s: str, lang: str) -> str:
    s = AUTO_DARK.sub("", s)
    s = s.replace("--bg: #fbfaf7;", "--bg: #ffffff;", 1)
    if theme.MARK not in s:
        s = s.replace('<meta charset="utf-8">\n', '<meta charset="utf-8">\n' + theme.HEAD, 1)
        s = s.replace("</style>", theme.CSS + "</style>", 1)
        s = re.sub(r'(<nav class="langbar"[^>]*>\n      <div class="lang-toggle">.*?\n      </div>\n)', lambda m: m.group(1) + "      " + theme.button(lang) + "\n", s, count=1, flags=re.S)
        s = s.replace("</body>", theme.BODY + "</body>", 1)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for rel, lang in PAGES.items():
        path = ROOT / rel
        old = path.read_text(encoding="utf-8")
        new = themed(old, lang)
        if new != old:
            stale.append(rel) if a.check else path.write_text(new, encoding="utf-8")
    if a.check and stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/apply_theme.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
