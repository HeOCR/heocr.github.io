"""Generate the English and Hebrew model downloads and app status pages."""

from __future__ import annotations

import argparse
from html import escape
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
MODEL_HUB = "https://huggingface.co/HeOCR/heocr-p-hist-measured"
FULL_MODEL_HUB = "https://huggingface.co/HeOCR/heocr-p-hist-full"
LITERATURE_HUB = "https://huggingface.co/HeOCR/heocr-literature-measured"
POINTED_HUB = "https://huggingface.co/HeOCR/heocr-pointed-measured"
MODERN_HUB = "https://huggingface.co/HeOCR/heocr-modern-measured"
QUICK_START_VERSION = "v1.1"
# (title, version, anchor, description key, hub, Zenodo DOI, held-out result link, result label key)
MODEL_RELEASES = (
    ("HeOCR modern MEASURED", "v1.0", "modern-v10", "modern", MODERN_HUB, "10.5281/zenodo.24615080",
     "benchmarks.html#p-mod-open", "pmod_benchmark"),
    ("HeOCR literature MEASURED", "v1.0", "literature-v10", "literature", LITERATURE_HUB, "10.5281/zenodo.24620176",
     "benchmarks.html#pby-h-open", "pbyh_benchmark"),
    ("HeOCR pointed MEASURED", "v1.0", "pointed-v10", "pointed", POINTED_HUB, "10.5281/zenodo.24620184",
     "benchmarks.html#pby-h-pointed", "pointed_benchmark"),
    ("HeOCR P-hist MEASURED", QUICK_START_VERSION, "phist-v11", "measured_latest", MODEL_HUB, "10.5281/zenodo.24581274",
     "benchmarks.html#p-hist-open-scores-filtered-pooled", "model_benchmark"),
    ("HeOCR P-hist MEASURED", "v1.0", "phist-v10", "measured_previous", MODEL_HUB, "10.5281/zenodo.24578440",
     f"{MODEL_HUB}/blob/v1.0/README.md#held-out-evaluation-old-printed-hebrew-unpointed", "model_benchmark"),
    ("HeOCR P-hist FULL", "v1.1-full", "phist-full-v11", "full_v11", FULL_MODEL_HUB, "10.5281/zenodo.24586339",
     None, None),
    ("HeOCR P-hist FULL", "v1.0-full", "phist-full-v10", "full_v10", FULL_MODEL_HUB, "10.5281/zenodo.24582845",
     None, None),
)
# The choice compass (site review 2, COPY-07): document type -> model card. Each line states only
# what that model's held-out table supports. Home (apply_shell.py) lists the same four.
COMPASS = (("modern-v10", "use_modern", "why_modern"), ("phist-v11", "use_phist", "why_phist"),
           ("literature-v10", "use_literature", "why_literature"), ("pointed-v10", "use_pointed", "why_pointed"))
FAMILIES = tuple(next(r for r in MODEL_RELEASES if r[2] == anchor) for anchor, _, _ in COMPASS)
QUICK_START = (
    "mkdir -p tessdata\n"
    "curl -fL -o tessdata/phist_v2.traineddata \\\n"
    f"  {MODEL_HUB}/resolve/{QUICK_START_VERSION}/phist_v2.traineddata\n"
    "tesseract page.png out -l phist_v2 --tessdata-dir ./tessdata --psm 3"
)
# The heocr package from PyPI (lead, 2026-11-28: heocr 0.3.0 release). `--download-model auto` fetches the four
# measured models once (sha256 checked). 0.3.0's CLI default is a modern-print model (not named on the site); `--ocr-model auto`
# is opt-in and experimental (lead, 2026-11-28).
PACKAGE_VERSION = "0.3.0"
PACKAGE_REPO = "https://github.com/HeOCR/heocr"
PACKAGE_PYPI = f"https://pypi.org/project/heocr/{PACKAGE_VERSION}/"
PACKAGE_INSTALL = ("pip install heocr\n"
                   "heocr --download-model auto\n"
                   "heocr file.pdf -o out.txt")
# The desktop release (HeOCR/heocr-desktop v0.3.0): the files and their SHA-256 as attached to the release.
DESKTOP_VERSION = "0.3.0"
DESKTOP_REPO = "https://github.com/HeOCR/heocr-desktop"
DESKTOP_DOWNLOADS = (
    ("macOS", "desktop_mac", f"HeOCR-{DESKTOP_VERSION}-macos.dmg",
     "8afa13f0cbf0e7e2dc169ae315c7ce156bad539365a3a425a495d0d9e49cb422"),
    ("Windows", "desktop_win", f"HeOCR-{DESKTOP_VERSION}-windows-x64.msi",
     "18cf6be53a0d652527cfdfe40b0b082696d1493cf5aa474217f9bae7bd963136"),
)
TESSERACT = "https://github.com/tesseract-ocr/tesseract"
T = {
    "en": {
        "title": "Download HeOCR",
        "models": "OCR models",
        "about": "HeOCR models are available now for modern printed documents (modern v1.0), historical unpointed print (P-hist v1.1), unpointed literary print (literature v1.0) and pointed literary print (pointed v1.0). Apache 2.0.",
        "compass": "Which model for your document?",
        "use_modern": "Modern printed document, unpointed",
        "why_modern": "Evaluated on the P-mod-open v0 held-out set.",
        "use_phist": "Old book, newspaper or law, unpointed",
        "why_phist": "Lowest error of every reader we measured on the P-hist-open v0.1 held-out set (C2), Google’s included.",
        "use_literature": "Literary print, unpointed",
        "why_literature": "Lowest error on the PBY-H v1 held-out set (corrected run); not shown better than Rivok Tesseract Lite.",
        "use_pointed": "Pointed (niqqud) print",
        "why_pointed": "Lowest error among the open readers we measured, statistically level with Rivok Tesseract Full, on a small set (8 works). Google’s readers are more accurate.",
        "variants": "MEASURED or FULL?",
        "variants_text": "MEASURED is the version our published held-out numbers belong to. FULL was also trained on our public test-set pages, so it has no independent score. It may be slightly stronger on similar material; this is not measured.",
        "package_text": "The heocr Python package reads a whole document (PDF, Word files and scans) and picks the right tool for each part. It needs Python 3.11 or later, and Tesseract 5 to read scans.",
        "package_install": "Install it from PyPI, then download HeOCR’s four measured models once (about 23 MB; each is checked against its pinned SHA-256). It then reads offline, with the default modern-print model.",
        "package_models": "For other print, choose the model: --ocr-model old-print, modern-literature or pointed. --ocr-model auto chooses for each document; it is experimental.",
        "package_repo": "HeOCR/heocr on GitHub",
        "quick_start": "Quick start",
        "advanced": "Advanced: use the traineddata directly",
        "quick_start_file": "The file for HeOCR P-hist MEASURED v1.1 is named phist_v2.traineddata; the release version is v1.1.",
        "instructions": "With Tesseract 5 and curl installed, save your page as page.png and run these commands in the same directory. The result is written to out.txt.",
        "experimental": "HeOCR’s handwriting models are still experimental.",
        "pmod_benchmark": "P-mod-open held-out result",
        "modern": "Modern unpointed printed documents. Evaluated on the P-mod-open v0 held-out set.",
        "benchmarks": "See all benchmarks",
        "model_benchmark": "Held-out result on P-hist-open (C2)",
        "pbyh_benchmark": "PBY-H held-out result",
        "pointed_benchmark": "PBY-H pointed held-out result",
        "literature": "Unpointed literary print. Evaluated on the PBY-H v1 held-out set.",
        "pointed": "Pointed (niqqud) literary print. Evaluated on the PBY-H v0.1 pointed held-out set, where Google’s readers score better.",
        "measured_latest": "Best / Latest. Evaluated on the P-hist-open held-out set (C2).",
        "measured_previous": "Previous version. Evaluated on the P-hist-open held-out set (C2).",
        "full_v10": "Also trained on our public test-set pages, so it has no independent score.",
        "apps": "Apps",
        "full_v11": "Also trained on our public test-set pages, so it has no independent score.",
        "coming": "In development.",
        "desktop_mac": "For macOS 13 or later, on Apple silicon and Intel. Signed and notarized by Apple.",
        "desktop_win": "For 64-bit Windows. This installer is not yet code-signed: when SmartScreen warns you, check the file against the SHA-256 below, then click More info and Run anyway.",
        "desktop_get": "Download {file}",
        "desktop_about": "The app reads on your computer and sends nothing anywhere. It starts on the modern-documents model; automatic model choice is experimental.",
        "notes": "Release notes",
        "releases": "Releases on GitHub",
        "code_signing": "Code signing policy",
        "privacy": "Privacy policy",
    },
    "he": {
        "title": "הורדת HeOCR",
        "models": "מודלים לזיהוי תווים",
        "about": "מודלים של HeOCR זמינים להורדה למסמכים מודרניים בדפוס (modern v1.0), לדפוס היסטורי לא מנוקד (P-hist v1.1), לספרות בדפוס לא מנוקד (literature v1.0) ולספרות בדפוס מנוקד (pointed v1.0), ברישיון Apache 2.0.",
        "compass": "איזה מודל מתאים למסמך שלכם?",
        "use_modern": "מסמך מודפס מודרני, ללא ניקוד",
        "why_modern": "נבדק על מערך המבחן P-mod-open v0.",
        "use_phist": "ספר, עיתון או חוק ישן, ללא ניקוד",
        "why_phist": "שיעור השגיאות הנמוך ביותר מבין כל המנועים שבדקנו על מערך המבחן P-hist-open v0.1 (C2), כולל אלה של Google.",
        "use_literature": "ספרות בדפוס, ללא ניקוד",
        "why_literature": "שיעור השגיאות הנמוך ביותר על מערך המבחן PBY-H v1 (ההרצה המתוקנת); לא הוכח שהוא טוב יותר מ־Rivok Tesseract Lite.",
        "use_pointed": "דפוס מנוקד",
        "why_pointed": "שיעור השגיאות הנמוך ביותר מבין המנועים הפתוחים שבדקנו, שקול סטטיסטית ל־Rivok Tesseract Full, במערך קטן (8 יצירות). המנועים של Google מדויקים יותר.",
        "variants": "MEASURED או FULL?",
        "variants_text": "MEASURED היא הגרסה שאליה שייכות התוצאות שפרסמנו על מערכי המבחן. FULL אומנה גם על עמודים ממערכי המבחן הפומביים שלנו, ולכן אין לה ציון בלתי תלוי. ייתכן שהיא מעט חזקה יותר על חומר דומה, אבל זה לא נמדד.",
        "package_text": "חבילת הפייתון heocr קוראת מסמך שלם (PDF, קובצי Word וסריקות) ובוחרת את הכלי המתאים לכל חלק בו. היא דורשת Python 3.11 ומעלה, ו־Tesseract 5 לקריאת סריקות.",
        "package_install": "התקינו אותה מ־PyPI, ואז הורידו פעם אחת את ארבעת המודלים המדודים של HeOCR (כ־23 MB; כל אחד נבדק מול ה־SHA-256 הקבוע שלו). מאז היא קוראת בלי אינטרנט, עם מודל ברירת המחדל לדפוס מודרני.",
        "package_models": "לדפוס מסוג אחר בחרו מודל: ‎--ocr-model old-print, ‏modern-literature או pointed. ‏‎--ocr-model auto בוחר מודל לכל מסמך, והוא ניסיוני.",
        "package_repo": "HeOCR/heocr ב־GitHub",
        "quick_start": "התחלה מהירה",
        "advanced": "מתקדם: שימוש ישיר בקובצי traineddata",
        "quick_start_file": "הקובץ של HeOCR P-hist MEASURED v1.1 נקרא phist_v2.traineddata, וגרסת השחרור היא v1.1.",
        "instructions": "התקינו Tesseract 5 ו־curl, שמרו את העמוד בשם page.png והריצו את הפקודות מאותה תיקייה. התוצאה תישמר בקובץ out.txt.",
        "experimental": "המודלים של HeOCR לכתב יד עדיין ניסיוניים.",
        "pmod_benchmark": "תוצאות על מערך המבחן P-mod-open",
        "modern": "מסמכים מודרניים בדפוס לא מנוקד. נבדק על מערך המבחן P-mod-open v0.",
        "benchmarks": "לכל מדדי ההערכה",
        "model_benchmark": "תוצאות על מערך המבחן P-hist-open (C2)",
        "pbyh_benchmark": "תוצאות על מערך המבחן PBY-H",
        "pointed_benchmark": "תוצאות על מערך המבחן המנוקד PBY-H",
        "literature": "ספרות בדפוס לא מנוקד. נבדק על מערך המבחן PBY-H v1.",
        "pointed": "ספרות בדפוס מנוקד. נבדק על מערך המבחן המנוקד PBY-H v0.1, שבו המנועים של Google משיגים תוצאות טובות יותר.",
        "measured_latest": "הגרסה הטובה והעדכנית ביותר. נבדקה על מערך המבחן P-hist-open (C2).",
        "measured_previous": "גרסה קודמת. נבדקה על מערך המבחן P-hist-open (C2).",
        "full_v10": "אומנה גם על עמודים ממערכי המבחן הפומביים שלנו, ולכן אין לה ציון בלתי תלוי.",
        "apps": "יישומים",
        "full_v11": "אומנה גם על עמודים ממערכי המבחן הפומביים שלנו, ולכן אין לה ציון בלתי תלוי.",
        "coming": "בפיתוח.",
        "desktop_mac": "ל־macOS 13 ומעלה, במחשבי Apple silicon ו־Intel. חתומה ומאושרת (notarized) על ידי Apple.",
        "desktop_win": "ל־Windows ‏64 ביט. המתקין עוד לא חתום בחתימת קוד: כשתופיע אזהרה של SmartScreen, בדקו את הקובץ מול ה־SHA-256 שלמטה, ואז לחצו על More info ועל Run anyway.",
        "desktop_get": "הורדת {file}",
        "desktop_about": "האפליקציה קוראת במחשב שלכם ולא שולחת דבר לשום מקום. היא מתחילה עם המודל למסמכים מודרניים; בחירת מודל אוטומטית היא ניסיונית.",
        "notes": "הערות הגרסה",
        "releases": "גרסאות ב־GitHub",
        "code_signing": "מדיניות חתימת קוד",
        "privacy": "מדיניות פרטיות",
    },
}


def page(lang: str) -> str:
    text = {key: escape(value) for key, value in T[lang].items()}
    model_cards = []
    for title, version, anchor, description, hub, doi, result, result_label in MODEL_RELEASES:
        benchmark = (f'<a href="{result}">{text[result_label]}</a>'
                     if result else "")
        model_cards.append(
            f'<div class="card" id="{anchor}"><h3><bdi dir="ltr">{title} {version}</bdi></h3>'
            f'<p>{text[description]}</p>'
            f'<div class="row"><a href="{hub}/tree/{version}">Hugging Face</a>'
            f'<a href="https://doi.org/{doi}">Zenodo</a>{benchmark}</div></div>\n'
        )
    titles = {anchor: f"{title} {version}" for title, version, anchor, *_ in MODEL_RELEASES}
    compass = "".join(
        f'<li><strong>{text[use]}:</strong> <a href="#{anchor}"><bdi dir="ltr">{titles[anchor]}</bdi></a>. {text[why]}</li>\n'
        for anchor, use, why in COMPASS
    )
    cards = "".join(
        f'<div class="card" id="{platform.lower()}"><h3><bdi dir="ltr">{platform} {DESKTOP_VERSION}</bdi></h3><p>{text[note]}</p>'
        f'<div class="row"><a href="{DESKTOP_REPO}/releases/download/v{DESKTOP_VERSION}/{name}">'
        f'{text["desktop_get"].replace("{file}", f"<bdi dir=\"ltr\">{name}</bdi>")}</a></div>'
        f'<p class="note">SHA-256 <code style="display: block; white-space: normal; word-break: break-all" dir="ltr">{digest}</code></p></div>\n'
        for platform, note, name, digest in DESKTOP_DOWNLOADS
    ) + (
        f'<div class="card"><h3>Android</h3><p>{text["coming"]}</p>'
        f'<div class="row"><a href="{DESKTOP_REPO}/releases">{text["releases"]}</a></div></div>\n'
    )
    return (
        shell.head(lang, text["title"], text["about"], "download")
        + shell.header(lang, "download")
        + '<main id="main" class="wrap doc">\n'
        + shell.page_head(text["title"], f'<p class="lede">{text["about"]}</p>')
        + f'<section id="apps">\n<h2>{text["apps"]}</h2>\n<div class="grid">\n{cards}</div>\n'
          f'<p>{text["desktop_about"]} <a href="{DESKTOP_REPO}/releases/tag/v{DESKTOP_VERSION}">{text["notes"]}</a></p>\n'
          f'<p><a href="code-signing.html">{text["code_signing"]}</a> · <a href="privacy.html">{text["privacy"]}</a></p>\n</section>\n'
        + f'<section id="choose">\n<h2>{text["compass"]}</h2>\n<ul class="compass">\n{compass}</ul>\n</section>\n'
        + f'<section id="quick-start">\n<h2>{text["quick_start"]}</h2>\n<p>{text["package_text"]}</p>\n'
          f'<p>{text["package_install"]}</p>\n<pre class="quick-start"><code>{escape(PACKAGE_INSTALL)}</code></pre>\n'
          f'<p>{text["package_models"]}</p>\n'
          f'<p><a href="{PACKAGE_PYPI}">PyPI</a> · <a href="{PACKAGE_REPO}">{text["package_repo"]}</a></p>\n</section>\n'
        + f'<section id="models">\n<h2>{text["models"]}</h2>\n<div class="grid">\n{"".join(model_cards)}</div>\n'
          f'<h3 id="variants">{text["variants"]}</h3>\n<p>{text["variants_text"]}</p>\n</section>\n'
        + f'<section id="tesseract">\n<h2>{text["advanced"]}</h2>\n'
          f'<p>{text["instructions"].replace("Tesseract 5", f'<a href="{TESSERACT}">Tesseract 5</a>', 1)}</p>\n'
          f'<pre class="quick-start"><code>{escape(QUICK_START)}</code></pre>\n'
          f'<p class="note">{text["quick_start_file"]}</p>\n</section>\n'
        + f'<p>{text["experimental"]} <a href="benchmarks.html">{text["benchmarks"]}</a></p>\n'
        + "</main>\n"
        + shell.footer([f'<p><a href="code-signing.html">{text["code_signing"]}</a></p>'], lang)
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
