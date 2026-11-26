"""Build redirects for old Hebrew URLs and superseded public design snapshots.

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
DESIGN_DIR = Path("design/brand-handover/site")
DESIGN_PAGES = ("home", "bench", "htext")
TEXT = {"he": "העמוד עבר. אם לא עברתם אוטומטית, ", "en": "This page moved. If you are not redirected, "}
LINK = {"he": "הקישור לעמוד החדש", "en": "open the updated page"}


def page(key: str, lang: str, rel: str) -> str:
    target = shell.page_url(lang, key)
    direction = "rtl" if lang == "he" else "ltr"
    return (f'<!doctype html>\n<html lang="{lang}" dir="{direction}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>HeOCR</title>\n'
            f'<meta http-equiv="refresh" content="0; url={rel}">\n<link rel="canonical" href="{target}">\n'
            f'</head>\n<body>\n<p>{TEXT[lang]}<a href="{rel}">{LINK[lang]}</a>.</p>\n</body>\n</html>\n')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    redirects = {
        Path(OLD_DIR) / name: (key, "he", "../" + ("" if key == "home" else name))
        for key, name in shell.PAGES.items()
    }
    for key in DESIGN_PAGES:
        name = shell.PAGES[key]
        redirects[DESIGN_DIR / name] = (key, "en", "../../../en/" + name)
        redirects[DESIGN_DIR / "he" / name] = (key, "he", "../../../../" + name)
    for path, (key, lang, rel) in redirects.items():
        expected = page(key, lang, rel)
        target = ROOT / path
        if a.check:
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                stale.append(str(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(expected, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_redirects.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
