"""Build the Download pages (download.html, he/download.html) for the HeOCR desktop app.

    python3 scripts/build_download.py           # write the pages
    python3 scripts/build_download.py --check   # exit 1 if a page is out of date

Standard library only. The shell (head, header, footer) is scripts/shell.py and the styles are site.css, as on
every page; the page uses existing components only (warn box, cards, buttons).
The download links point at the desktop app's latest GitHub release; they work once a release is
published (that waits for the release gate's verdict and the maintainers' go).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402  (head, header, footer: one source for every page)

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/HeOCR/heocr-desktop"
VERSION = "0.1.0"
MAC = f"{REPO}/releases/latest/download/HeOCR-{VERSION}-macos.dmg"
WIN = f"{REPO}/releases/latest/download/HeOCR-{VERSION}-windows-x64.msi"
LICENSES = f"{REPO}/blob/main/THIRD_PARTY_LICENSES.md"
POLICY = f"{REPO}/blob/main/docs/code-signing-policy.md"
e = html.escape

T = {
    "en": {
        "title": "Download HeOCR",
        "desc": "HeOCR for macOS and Windows: Hebrew text out of PDFs, Word documents and images, fully offline.",
        "lede": "Drop in a PDF, a Word document or an image, and get its Hebrew text out, with its headings, paragraphs and tables.",
        "offline": "<strong>Fully offline.</strong> Your files never leave your computer. The app makes no network connections and collects no data: no telemetry, no analytics, no update checks.",
        "mac": "macOS", "mac_req": "macOS 13 or later. One app for Apple silicon and Intel. Signed with an Apple Developer ID and notarized by Apple.",
        "win": "Windows", "win_req": "Windows 10 or 11, 64-bit.",
        "get": "Download", "soon": "The first release is being prepared.",
        "what_h": "What it does",
        "what": [
            "Opens PDF, Word (DOCX) and image files (PNG, JPEG, TIFF and more), and also Excel (XLSX), PowerPoint (PPTX) and saved web pages: drag one onto the window, or use the open button.",
            "Shows the text right to left, with headings, paragraphs and tables, and says how each page was read: from the PDF's own text layer, by OCR, or from the Word document.",
            "Copies the text, or saves it as plain text, Markdown, or heocr's full JSON record.",
            "Shows progress page by page for long PDFs, with a Cancel button.",
            "Its interface is in Hebrew or English, following your system, with a toggle.",
        ],
        "notes_h": "Good to know",
        "notes": [
            "OCR text is a reading, not a verified transcript: check names and numbers.",
            "Older Word files (.doc), RTF and OpenDocument files are not supported yet: reading them needs LibreOffice, which the app does not include (its licence is copyleft). Open the file in Word or <a href=\"https://www.libreoffice.org\">LibreOffice</a> and save it as DOCX or PDF.",
            "Windows may warn that the installer is from an unknown publisher, because it is not yet code-signed. Choose “More info”, then “Run anyway”.",
        ],
        "sign_h": "Code signing policy",
        "sign": [
            "Free code signing provided by <a href=\"https://about.signpath.io\">SignPath.io</a>, certificate by <a href=\"https://signpath.org\">SignPath Foundation</a>. Only installers built by GitHub Actions from the public source are signed, and each signing is approved by hand.",
            "Team roles: committers and reviewers, Shay Palachy Affek (<a href=\"https://github.com/shaypal5\">@shaypal5</a>), with AI coding agents that work through reviewed pull requests; approver, Shay Palachy Affek.",
            "Privacy: this program will not transfer any information to other networked systems unless specifically requested by the user or the person installing or operating it. HeOCR has no network feature at all.",
        ],
        "sign_more": "The full policy",
        "inside_h": "Inside",
        "inside": f"The app is a window around <a href=\"https://github.com/HeOCR/heocr\">heocr</a>, HeOCR's open pipeline for Hebrew documents, with Tesseract OCR and its Hebrew model bundled. Everything in it is under a permissive licence: <a href=\"{LICENSES}\">the full list</a>. Source: <a href=\"{REPO}\">HeOCR/heocr-desktop</a> (Apache-2.0).",
    },
    "he": {
        "title": "הורדת HeOCR",
        "desc": "HeOCR ל־macOS ול־Windows: טקסט עברי מתוך קובצי PDF, מסמכי Word ותמונות, בלי אינטרנט.",
        "lede": "גוררים קובץ PDF, מסמך Word או תמונה, ומקבלים את הטקסט העברי שבו, עם הכותרות, הפסקאות והטבלאות.",
        "offline": "<strong>עובד במלואו בלי אינטרנט.</strong> הקבצים שלכם לא יוצאים מהמחשב. האפליקציה אינה מתחברת לרשת ואינה אוספת נתונים: בלי טלמטריה, בלי אנליטיקה, בלי בדיקת עדכונים.",
        "mac": "macOS", "mac_req": "macOS 13 ואילך. אפליקציה אחת למעבדי Apple ול־Intel. חתומה ב־Apple Developer ID ומאושרת (notarized) על ידי Apple.",
        "win": "Windows", "win_req": "Windows 10 או 11, ‏64 סיביות.",
        "get": "הורדה", "soon": "הגרסה הראשונה בהכנה.",
        "what_h": "מה היא עושה",
        "what": [
            "פותחת קובצי PDF, ‏Word ‏(DOCX) ותמונות (PNG, ‏JPEG, ‏TIFF ועוד), וגם Excel ‏(XLSX), ‏PowerPoint ‏(PPTX) ודפי אינטרנט שמורים: גוררים קובץ לחלון, או לוחצים על כפתור הפתיחה.",
            "מציגה את הטקסט מימין לשמאל, עם כותרות, פסקאות וטבלאות, ואומרת איך נקרא כל עמוד: משכבת הטקסט של ה־PDF, בזיהוי תווים, או ממסמך ה־Word.",
            "מעתיקה את הטקסט, או שומרת אותו כטקסט פשוט, כ־Markdown או כרשומת ה־JSON המלאה של heocr.",
            "מציגה התקדמות עמוד אחר עמוד בקובצי PDF ארוכים, עם כפתור ביטול.",
            "הממשק בעברית או באנגלית, לפי שפת המערכת, עם מעבר בין השפות.",
        ],
        "notes_h": "כדאי לדעת",
        "notes": [
            "טקסט מזיהוי תווים הוא קריאה ולא תמלול מאומת: בדקו שמות ומספרים.",
            "קובצי Word ישנים (‎.doc), ‏RTF וקובצי OpenDocument עדיין לא נתמכים: קריאתם דורשת את LibreOffice, שאינו כלול באפליקציה (הרישיון שלו הוא קופילפט). פתחו את הקובץ ב־Word או ב־<a href=\"https://www.libreoffice.org\">LibreOffice</a> ושמרו אותו כ־DOCX או כ־PDF.",
            "ייתכן ש־Windows יזהיר שהמתקין ממפרסם לא מוכר, כי הוא עדיין לא חתום. בחרו „מידע נוסף” ואז „הפעל בכל זאת”.",
        ],
        "sign_h": "מדיניות חתימת קוד",
        "sign": [
            "חתימת קוד חינמית באדיבות <a href=\"https://about.signpath.io\">SignPath.io</a>, תעודה מאת <a href=\"https://signpath.org\">SignPath Foundation</a>. נחתמים רק מתקינים שנבנו ב־GitHub Actions מקוד המקור הפומבי, וכל חתימה מאושרת ידנית.",
            "תפקידים בצוות: כותבי קוד ובודקים, שי פלצ'י אפק (<a href=\"https://github.com/shaypal5\">@shaypal5</a>), עם סוכני קוד מבוססי בינה מלאכותית שעובדים דרך בקשות משיכה שנבדקות; מאשר חתימות, שי פלצ'י אפק.",
            "פרטיות: התוכנה לא תעביר מידע למערכות אחרות ברשת, אלא אם המשתמש או מי שמתקין או מפעיל אותה ביקשו זאת במפורש. ל־HeOCR אין שום יכולת רשת.",
        ],
        "sign_more": "המדיניות המלאה",
        "inside_h": "מה בפנים",
        "inside": f"האפליקציה היא חלון סביב <a href=\"https://github.com/HeOCR/heocr\">heocr</a>, צינור הקוד הפתוח של HeOCR למסמכים בעברית, עם מנוע זיהוי התווים Tesseract והמודל העברי שלו. כל מה שבתוכה ברישיון מתירני: <a href=\"{LICENSES}\">הרשימה המלאה</a>. קוד המקור: <a href=\"{REPO}\">HeOCR/heocr-desktop</a> ‏(Apache-2.0).",
    },
}


SHIELD = ('<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.6l5 2v4c0 3.2-2.1 5.8-5 6.8-2.9-1-5-3.6-5-6.8v-4l5-2z"></path>'
          '<path d="M5.6 8l1.7 1.7L10.6 6.3"></path></svg>')


def page(lang: str) -> str:
    t = T[lang]
    w = []
    w.append(shell.head(lang, e(t["title"]), e(t["desc"]), "download"))
    w.append(shell.header(lang, "download"))
    w.append(shell.page_head(e(t["title"]), f'<p class="lede">{e(t["lede"])}</p>'))
    w.append('<main id="main" class="wrap doc">\n')
    w.append(f'<p class="warn">{SHIELD}<span>{t["offline"]}</span></p>\n')
    w.append('<div class="grid">\n')
    for key, href in (("mac", MAC), ("win", WIN)):
        w.append(f'  <div class="card"><h3>{e(t[key])}</h3><p>{e(t[key + "_req"])}</p>'
                 f'<div class="row"><a class="btn primary" href="{href}">{e(t["get"])} {e(t[key])}</a></div></div>\n')
    w.append(f'</div>\n<p class="note">{e(t["soon"])}</p>\n')
    w.append(f'<section id="what">\n<h2>{e(t["what_h"])}</h2>\n<ul>\n' + "".join(f"  <li>{e(x)}</li>\n" for x in t["what"]) + "</ul>\n</section>\n")
    w.append(f'<section id="notes">\n<h2>{e(t["notes_h"])}</h2>\n<ul>\n' + "".join(f"  <li>{x}</li>\n" for x in t["notes"]) + "</ul>\n</section>\n")
    w.append(f'<section id="code-signing">\n<h2>{e(t["sign_h"])}</h2>\n' + "".join(f"<p>{x}</p>\n" for x in t["sign"])
             + f'<p><a href="{POLICY}">{e(t["sign_more"])}</a></p>\n</section>\n')
    w.append(f'<section id="inside">\n<h2>{e(t["inside_h"])}</h2>\n<p>{t["inside"]}</p>\n</section>\n')
    w.append("</main>\n")
    w.append(shell.footer([f'<p><a href="{REPO}">HeOCR/heocr-desktop</a> · <a href="./">HeOCR</a></p>']))
    w.append(shell.tail(lang))
    return "".join(w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    stale = []
    for lang, path in (("en", ROOT / "download.html"), ("he", ROOT / "he" / "download.html")):
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
