"""Build the redirect pages at the old Hebrew URLs (he/*.html), which moved to the site root.

    python3 scripts/build_redirects.py           # write the pages
    python3 scripts/build_redirects.py --check   # fails if a committed page differs

Hebrew became the default language: the Hebrew pages are at the root, English is under en/. The old
/he/... URLs keep working through these small pages: meta refresh, rel=canonical to the new URL, and a plain
link; no JavaScript. Standard library only, on scripts/shell.py (the page list and URLs).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OLD_DIR = "he"
TEXT = "העמוד עבר. אם לא עברתם אוטומטית, "
LINK = "הקישור לעמוד החדש"


def page(key: str) -> str:
    target = shell.page_url("he", key)
    rel = "../" + ("" if shell.PAGES[key] == "index.html" else shell.PAGES[key])
    return (f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>HeOCR</title>\n'
            f'<meta http-equiv="refresh" content="0; url={rel}">\n<link rel="canonical" href="{target}">\n'
            f'</head>\n<body>\n<p>{TEXT}<a href="{rel}">{LINK}</a>.</p>\n</body>\n</html>\n')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for key, name in shell.PAGES.items():
        path = ROOT / OLD_DIR / name
        s = page(key)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(f"{OLD_DIR}/{name}")
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_redirects.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
