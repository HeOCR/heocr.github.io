"""Build the privacy policy pages (privacy.html, en/privacy.html) for the HeOCR apps.

    python3 scripts/build_privacy.py           # write the pages
    python3 scripts/build_privacy.py --check   # exit 1 if a page is out of date

Standard library only, on the site's shell (scripts/shell.py) and styles (site.css). The Google Play
listing links here; it must say what the apps do with data, which is nothing.
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
ISSUES = f"{REPO}/issues"
EFFECTIVE = "2026-11-19"
e = html.escape

T = {
    "en": {
        "title": "Privacy policy",
        "desc": "The HeOCR apps collect no data: documents are read on your device and never sent anywhere.",
        "lede": "For the HeOCR apps: HeOCR for macOS and Windows, and HeOCR for Android.",
        "short": "<strong>The HeOCR apps collect no personal data, and send nothing anywhere.</strong> There is no account, no analytics, no telemetry, no advertising, no crash reporting and no update check.",
        "sections": [
            ("Your documents", [
                "Documents, photos and images you open in HeOCR are read on your own device, and never leave it.",
                "The desktop app refuses every network connection itself. The Android app has no internet permission, so Android blocks every connection it might try.",
                "On Android, a file you open or share to HeOCR is copied into the app's private storage to be read, and replaced by the next one. Removing the app removes it.",
            ]),
            ("The camera (Android)", [
                "HeOCR asks for the camera only when you tap “Take a photo”. The photo is read on your phone, kept only in the app's private storage, and replaced by the next one.",
            ]),
            ("Copying and saving", [
                "“Copy” puts the text on your device's clipboard, where other apps can read it, as with any copy. Files you save go where you choose.",
            ]),
            ("App stores and downloads", [
                "Google Play, F-Droid and GitHub, where you download HeOCR, may collect their own data when you do. Their privacy policies apply to that, not this one.",
            ]),
            ("This website", [
                "heocr.github.io is hosted on GitHub Pages, which may log visits under GitHub's privacy statement, and loads its fonts from Google Fonts. The site sets no cookies; your night-mode choice is kept in your browser's local storage only.",
            ]),
            ("Changes and contact", [
                f"Effective {EFFECTIVE}. Any change will be published on this page first. Questions: <a href=\"{ISSUES}\">open an issue</a> on HeOCR/heocr-desktop.",
            ]),
        ],
    },
    "he": {
        "title": "מדיניות פרטיות",
        "desc": "אפליקציות HeOCR אינן אוספות מידע: המסמכים נקראים במכשיר שלכם ולא נשלחים לשום מקום.",
        "lede": "לאפליקציות HeOCR: ‏HeOCR ל־macOS ול־Windows, ו־HeOCR ל־Android.",
        "short": "<strong>אפליקציות HeOCR אינן אוספות מידע אישי, ואינן שולחות דבר לשום מקום.</strong> אין חשבון, אין אנליטיקה, אין טלמטריה, אין פרסומות, אין דיווח קריסות ואין בדיקת עדכונים.",
        "sections": [
            ("המסמכים שלכם", [
                "מסמכים, צילומים ותמונות שאתם פותחים ב־HeOCR נקראים במכשיר שלכם, ולא יוצאים ממנו.",
                "אפליקציית המחשב חוסמת בעצמה כל חיבור לרשת. לאפליקציית Android אין הרשאת אינטרנט, כך ש־Android חוסמת כל חיבור שהיא עלולה לנסות.",
                "ב־Android, קובץ שאתם פותחים או משתפים ל־HeOCR מועתק לאחסון הפרטי של האפליקציה כדי להיקרא, ומוחלף בקובץ הבא. הסרת האפליקציה מוחקת אותו.",
            ]),
            ("המצלמה (Android)", [
                "HeOCR מבקשת גישה למצלמה רק כשאתם לוחצים על „צילום”. הצילום נקרא בטלפון, נשמר רק באחסון הפרטי של האפליקציה, ומוחלף בצילום הבא.",
            ]),
            ("העתקה ושמירה", [
                "„העתקה” שמה את הטקסט בלוח ההעתקה של המכשיר, שם אפליקציות אחרות יכולות לקרוא אותו, כמו בכל העתקה. קבצים שאתם שומרים נשמרים היכן שבחרתם.",
            ]),
            ("חנויות אפליקציות והורדות", [
                "‏Google Play, ‏F-Droid ו־GitHub, שמהם מורידים את HeOCR, עשויים לאסוף מידע משלהם בזמן ההורדה. על כך חלה מדיניות הפרטיות שלהם, לא זו.",
            ]),
            ("האתר הזה", [
                "האתר heocr.github.io מתארח ב־GitHub Pages, שעשוי לרשום ביקורים לפי הצהרת הפרטיות של GitHub, וטוען את הגופנים שלו מ־Google Fonts. האתר אינו שומר עוגיות; הבחירה במצב לילה נשמרת רק באחסון המקומי של הדפדפן.",
            ]),
            ("שינויים ויצירת קשר", [
                f"בתוקף מ־{EFFECTIVE}. כל שינוי יפורסם קודם בעמוד הזה. שאלות: <a href=\"{ISSUES}\">פתחו issue</a> ב־HeOCR/heocr-desktop.",
            ]),
        ],
    },
}


def page(lang: str) -> str:
    t = T[lang]
    w = [
        shell.head(lang, e(t["title"]), e(t["desc"]), "privacy"),
        shell.header(lang, "privacy"),
        shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p>'),
        '<main id="main" class="wrap doc">\n',
        f'<p class="warn"><span>{t["short"]}</span></p>\n',
    ]
    for heading, paragraphs in t["sections"]:
        w.append(f"<section>\n<h2>{e(heading)}</h2>\n" + "".join(f"<p>{p}</p>\n" for p in paragraphs) + "</section>\n")
    w.append("</main>\n")
    w.append(shell.footer([f'<p><a href="{REPO}">HeOCR/heocr-desktop</a> · <a href="./">HeOCR</a></p>'], lang))
    w.append(shell.tail(lang))
    return "".join(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for lang, path in (("he", ROOT / "privacy.html"), ("en", ROOT / "en" / "privacy.html")):
        s = page(lang)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_privacy.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
