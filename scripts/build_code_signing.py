"""Build the code-signing policy pages (code-signing.html, en/code-signing.html) for the HeOCR desktop app.

    python3 scripts/build_code_signing.py           # write the pages
    python3 scripts/build_code_signing.py --check   # exit 1 if a page is out of date

Site review 2, ARCH-04 / COPY-10: the policy moved here from the home page, which links to it from its
footer and its apps section. It names no signing provider: no Windows certificate is issued yet.
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/HeOCR/heocr-desktop"
RELEASES = f"{REPO}/releases"
POLICY = f"{REPO}/blob/main/docs/code-signing-policy.md"
SHAY = '<a href="https://github.com/shaypal5">@shaypal5</a>'
e = html.escape

T = {
    "en": {
        "title": "Code signing policy",
        "desc": "How the HeOCR desktop app for macOS and Windows is built and signed.",
        "lede": "For the HeOCR desktop app for macOS and Windows, which is in development.",
        "sections": [
            ("Status", [
                f"The app is not released yet. To hear when it is, watch <a href=\"{REPO}\">HeOCR/heocr-desktop</a> on GitHub "
                f"(Watch → Custom → Releases), or see its <a href=\"{RELEASES}\">releases page</a>.",
            ]),
            ("What is signed", [
                "Only installers built by GitHub Actions from the public source are signed, and each signing is approved by hand.",
                "macOS: signed with an Apple Developer ID and notarized by Apple.",
                "Windows: the installers are not code-signed yet. Once a certificate is issued, this page will name the signer "
                "and the certificate holder.",
            ]),
            ("Team roles", [
                f"Committers and reviewers: Shay Palachy Affek ({SHAY}), with AI coding agents that work through reviewed pull "
                "requests. Approver: Shay Palachy Affek.",
            ]),
            ("Privacy", [
                "This program will not transfer any information to other networked systems unless specifically requested by "
                "the user or the person installing or operating it. The app has no network feature at all. "
                f"See also the <a href=\"privacy.html\">privacy policy</a> and <a href=\"{POLICY}\">the full signing policy</a>.",
            ]),
        ],
    },
    "he": {
        "title": "מדיניות חתימת קוד",
        "desc": "איך נבנית ונחתמת אפליקציית HeOCR למחשב, ל־macOS ול־Windows.",
        "lede": "לאפליקציית HeOCR למחשב, ל־macOS ול־Windows, שנמצאת בפיתוח.",
        "sections": [
            ("מצב", [
                f"האפליקציה עוד לא שוחררה. כדי לדעת כשתשוחרר, עקבו אחרי <a href=\"{REPO}\">HeOCR/heocr-desktop</a> ב־GitHub "
                f"(Watch ← Custom ← Releases), או ראו את <a href=\"{RELEASES}\">עמוד הגרסאות</a>.",
            ]),
            ("מה נחתם", [
                "נחתמים רק מתקינים שנבנו ב־GitHub Actions מקוד המקור הפומבי, וכל חתימה מאושרת ידנית.",
                "macOS: חתומה ב־Apple Developer ID ומאושרת (notarized) על ידי Apple.",
                "Windows: המתקינים עוד לא חתומים. כשתונפק תעודה, העמוד הזה יציין מי חותם ומי מחזיק בתעודה.",
            ]),
            ("תפקידים בצוות", [
                f"כותבי קוד ובודקים: שי פלצ'י אפק ({SHAY}), עם סוכני קוד מבוססי בינה מלאכותית שעובדים דרך בקשות משיכה "
                "שנבדקות. מאשר חתימות: שי פלצ'י אפק.",
            ]),
            ("פרטיות", [
                "התוכנה לא תעביר מידע למערכות אחרות ברשת, אלא אם המשתמש או מי שמתקין או מפעיל אותה ביקשו זאת במפורש. "
                "לאפליקציה אין שום יכולת רשת. "
                f"ראו גם את <a href=\"privacy.html\">מדיניות הפרטיות</a> ואת <a href=\"{POLICY}\">מדיניות החתימה המלאה</a>.",
            ]),
        ],
    },
}


def page(lang: str) -> str:
    t = T[lang]
    w = [
        shell.head(lang, e(t["title"]), e(t["desc"]), "code-signing"),
        shell.header(lang, "code-signing"),
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p>'),
        '<main id="main" class="wrap doc">\n',
    ]
    for heading, paragraphs in t["sections"]:
        w.append(f"<section>\n<h2>{e(heading)}</h2>\n" + "".join(f"<p>{p}</p>\n" for p in paragraphs) + "</section>\n")
    w.append("</main>\n")
    w.append(shell.footer([f'<p><a href="{REPO}">HeOCR/heocr-desktop</a> · <a href="./">HeOCR</a></p>']))
    w.append(shell.tail(lang))
    return "".join(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for lang, path in (("he", ROOT / "code-signing.html"), ("en", ROOT / "en" / "code-signing.html")):
        s = page(lang)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_code_signing.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
