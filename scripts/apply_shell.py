"""Keep the shared shell of the hand-written pages in sync with scripts/shell.py.

    python3 scripts/apply_shell.py           # rewrite the shell blocks of index.html, rights.html (HE at the root, EN under en/)
    python3 scripts/apply_shell.py --check   # exit 1 if a page's shell differs from shell.py

The hand-written pages carry four marked blocks, which this script owns:

    <!-- shell:head -->    … fonts, site.css, theme script, icons, link previews …   <!-- /shell:head -->
    <!-- shell:header -->  … skip link and site header …                              <!-- /shell:header -->
    <!-- shell:partner -->  … the footer's partnership strip …                       <!-- /shell:partner -->
    <!-- shell:tail -->    … theme.js …                                               <!-- /shell:tail -->

The home pages also take their release status and introduction from this builder.
The generated pages (benchmarks, htext) get the same blocks from their build scripts.
"""
from __future__ import annotations

import argparse
import html
import json
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
        "intro": "HeOCR is an open project for getting Hebrew text out of any document: PDF and Office files, web pages, scans and photos. The code, the models and the data are open, and the tools run on your own computer or phone.",
        "apps": "Desktop app",
        "apps_text": "HeOCR for macOS and Windows is in development. To hear when it is out, watch HeOCR/heocr-desktop on GitHub (Watch → Custom → Releases).",
        "apps_releases": "Releases",
        "code_signing": "Code signing policy",
        "privacy": "Privacy policy",
        "rights_link": "Rights &amp; takedown",
        "models": "Models and pipeline",
        "status": "Four HeOCR OCR models for Tesseract 5, one for each kind of printed document.",
        "model_link": "Get the OCR weights",
        "download": "Download",
        "sources": "The releases use public-domain or openly licensed sources. Each item keeps its source and credit.",
        "wikisource": "Hebrew Wikisource text appears in the training corpora and in line pairs. Releases link to source revisions and record the CC BY-SA terms.",
        "tagline": "Hebrew text out of any document",
        "bench": "Benchmarks",
        "flow_aria": "How the parts fit together",
        "flow": ("Open scans &amp; text", "Generators", "Datasets", "Trained models", "Tools &amp; apps"),
        "start": "How to use HeOCR",
        "start_cards": (
            ("No code: the desktop app", "An offline app for macOS and Windows that reads Hebrew documents on your own computer, without uploading them. In development.", "download.html#apps", "Follow its release"),
            ("For developers and researchers", "Install heocr from PyPI (pip install heocr), download the four models once, and read PDFs, Word files and scans. Or use the models directly in Tesseract 5.", "download.html#quick-start", "Quick start"),
        ),
        "code": "Code",
        "groups": (
            ("Tools", (
                ("heocr", "Python package and CLI: Hebrew text out of PDFs, Office files, web pages, scans and photos."),
                ("heocr-desktop", "HeOCR's apps for Mac, Windows and Android: Hebrew text out of documents, fully offline."),
            )),
            ("Models and data", (
                ("heocr-engine", "The models: training and packaging Hebrew OCR models."),
                ("htext", "Public-domain and openly licensed Hebrew text, for training Hebrew OCR."),
                ("hocrsyngen", "A generator of synthetic Hebrew OCR training data: lines and pages."),
                ("hdocsyngen", "A generator of synthetic Hebrew documents: Office files and PDFs, with exact structure."),
            )),
            ("Review and infrastructure", (
                ("heocr-review", "Check and correct Hebrew text against page scans, line by line."),
                ("heocr-compute", "Runs HeOCR's training jobs on rented machines: open data only, within a budget."),
            )),
        ),
        "help": "Want to help? Open an issue or a pull request in any of the repositories.",
        "demo": "What it looks like",
        "demo_caption": "Six lines of rabbinic print from Sefer ehilat Mosheh (Lublin, 1906; public domain), as scanned by the University of Toronto for the Internet Archive. Beside them, the text HeOCR P-hist MEASURED v1.1 read, unedited, mistakes included.",
        "demo_note": "An illustration, not a measurement. The page is in none of our training, development or test sets.",
        "demo_alt": "A scanned strip of six lines of Hebrew rabbinic print",
        "demo_source": "The page on the Internet Archive",
        "demo_model": "The model",
    },
    "he": {
        "intro": "HeOCR הוא פרויקט פתוח להוצאת טקסט עברי מכל מסמך: קובצי PDF ואופיס, דפי אינטרנט, סריקות וצילומים. הקוד, המודלים והנתונים פתוחים, והכלים רצים על המחשב או הטלפון שלכם.",
        "apps": "אפליקציה למחשב",
        "apps_text": "HeOCR ל־macOS ול־Windows נמצאת בפיתוח. כדי לדעת כשתצא, עקבו אחרי HeOCR/heocr-desktop ב־GitHub (Watch ← Custom ← Releases).",
        "apps_releases": "גרסאות",
        "code_signing": "מדיניות חתימת קוד",
        "privacy": "מדיניות פרטיות",
        "rights_link": "זכויות והסרה",
        "models": "מודלים וצינור העיבוד",
        "status": "ארבעה מודלים של HeOCR לזיהוי תווים עם Tesseract 5, אחד לכל סוג של מסמך מודפס.",
        "model_link": "הורדת משקלי המודל",
        "download": "הורדה",
        "sources": "הגרסאות משתמשות במקורות בנחלת הכלל או ברישיון פתוח. כל פריט שומר את המקור ואת הקרדיט שלו.",
        "wikisource": "טקסט מוויקיטקסט העברית מופיע במאגרי האימון ובזוגות השורות. בכל גרסה יש קישורים למקורות ותיעוד של תנאי CC BY-SA.",
        "tagline": "טקסט עברי מכל מסמך",
        "bench": "מדדי ביצועים",
        "flow_aria": "איך החלקים מתחברים",
        "flow": ("סריקות וטקסטים פתוחים", "מחוללים", "מאגרי נתונים", "מודלים מאומנים", "כלים ויישומים"),
        "start": "איך משתמשים ב־HeOCR",
        "start_cards": (
            ("בלי קוד: אפליקציה למחשב", "אפליקציה ל־macOS ול־Windows שקוראת מסמכים בעברית במחשב שלכם, בלי אינטרנט ובלי להעלות אותם לשום מקום. בפיתוח.", "download.html#apps", "מעקב אחרי השחרור"),
            ("למפתחים ולחוקרים", "התקינו את heocr מ־PyPI ‏(pip install heocr), הורידו פעם אחת את ארבעת המודלים, וקראו קובצי PDF, קובצי Word וסריקות. אפשר גם להשתמש במודלים ישירות ב־Tesseract 5.", "download.html#quick-start", "התחלה מהירה"),
        ),
        "code": "קוד",
        "groups": (
            ("כלים", (
                ("heocr", "חבילת פייתון וכלי שורת פקודה: טקסט עברי מקובצי PDF, אופיס, דפי אינטרנט, סריקות וצילומים."),
                ("heocr-desktop", "האפליקציות של HeOCR למק, לווינדוס ולאנדרואיד: טקסט עברי ממסמכים, בלי אינטרנט."),
            )),
            ("מודלים ונתונים", (
                ("heocr-engine", "המודלים: אימון ואריזה של מודלי זיהוי טקסט עברי."),
                ("htext", "טקסט עברי בנחלת הכלל וברישיון פתוח, לאימון OCR בעברית."),
                ("hocrsyngen", "מחולל נתונים סינתטיים לאימון זיהוי טקסט עברי: שורות ועמודים."),
                ("hdocsyngen", "מחולל מסמכים סינתטיים בעברית: קובצי Office ו-PDF, עם מבנה מדויק."),
            )),
            ("בדיקה ותשתית", (
                ("heocr-review", "בודקים ומתקנים טקסט עברי מול סריקות של דפים, שורה אחר שורה."),
                ("heocr-compute", "מריץ את עבודות האימון של HeOCR על מכונות שכורות: מידע פתוח בלבד, בתוך תקציב."),
            )),
        ),
        "help": "רוצים לעזור? פתחו issue או pull request באחד המאגרים.",
        "demo": "איך זה נראה",
        "demo_caption": "שש שורות בדפוס רבני מתוך Sefer ehilat Mosheh (לובלין, 1906; נחלת הכלל), בסריקה של אוניברסיטת טורונטו עבור Internet Archive. לצידן הטקסט ש־HeOCR P-hist MEASURED v1.1 קרא, כמו שהוא, עם הטעויות.",
        "demo_note": "המחשה, לא מדידה. העמוד אינו באף אחד ממערכי האימון, הפיתוח או המבחן שלנו.",
        "demo_alt": "רצועה סרוקה של שש שורות בדפוס רבני עברי",
        "demo_source": "העמוד ב־Internet Archive",
        "demo_model": "המודל",
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
    # The code-signing policy has its own page (site review 2, ARCH-04 / COPY-10); home keeps a short
    # apps section in its place, and the footer links to the policy.
    desktop = "https://github.com/HeOCR/heocr-desktop"
    text = re.sub(
        r'^  <section id="(?:code-signing|apps)">.*?^  </section>',
        lambda _: (
            '  <section id="apps">\n'
            f'    <h2>{html.escape(t["apps"])}</h2>\n'
            f'    <p class="sub">{html.escape(t["apps_text"])}</p>\n'
            f'    <p><a href="{desktop}/releases">{html.escape(t["apps_releases"])}</a> · '
            f'<a href="code-signing.html">{html.escape(t["code_signing"])}</a> · '
            f'<a href="privacy.html">{html.escape(t["privacy"])}</a></p>\n'
            '  </section>'
        ),
        text, count=1, flags=re.M | re.S,
    )
    text = re.sub(
        r'<p><a href="rights.html">[^<]*</a>(?: · <a href="code-signing.html">[^<]*</a>)?</p>',
        lambda _: (f'<p><a href="rights.html">{t["rights_link"]}</a> · '
                   f'<a href="code-signing.html">{html.escape(t["code_signing"])}</a></p>'),
        text, count=1,
    )
    return re.sub(
        r'(<h3><a href="https://he.wikisource.org">[^<]+</a></h3>\s*<p>).*?(</p>)',
        lambda m: m[1] + html.escape(t["wikisource"]) + m[2],
        text,
        count=1,
    )


ORG = "https://github.com/HeOCR"


DEMO = ROOT / "demo" / "demo.json"


def demo_section(lang: str) -> str:
    """A cleared public-domain strip and what a released model read on it (site review 2, ARCH-02 §2).

    demo/demo.json records the source, the clearance receipt, the model, the command and the output; the
    image must still be the cleared file. Captioned as an illustration: no metric."""
    import hashlib

    t, demo = HOME[lang], json.loads(DEMO.read_text(encoding="utf-8"))
    image = demo["image"]
    if hashlib.sha256((ROOT / image["path"]).read_bytes()).hexdigest() != image["sha256"]:
        raise SystemExit(f"{image['path']} is not the cleared demo image")
    width, height = image["px"]
    lines = "".join(f"        <p>{html.escape(line)}</p>\n" for line in demo["output"])
    return (
        f'\n  <section id="demo">\n    <h2>{html.escape(t["demo"])}</h2>\n    <div class="grid">\n'
        f'      <div class="card">\n        <img src="{shell.prefix(lang)}{image["path"]}" width="{width}" height="{height}" '
        f'alt="{html.escape(t["demo_alt"])}" style="width: 100%; height: auto">\n      </div>\n'
        f'      <div class="card" lang="he" dir="rtl">\n{lines}      </div>\n    </div>\n'
        f'    <p class="sub">{html.escape(t["demo_caption"])}</p>\n'
        f'    <p class="sub">{html.escape(t["demo_note"])} <a href="{demo["source"]["url"]}">{html.escape(t["demo_source"])}</a> · '
        f'<a href="{demo["model"]["url"]}">{html.escape(t["demo_model"])}</a></p>\n  </section>\n'
    )


def home_layout(lang: str, text: str) -> str:
    """The home hero, "How to use" and code sections (site review 2, COPY-02/03/04/06, ARCH-02 §1).

    The tagline, intro, repo groups, one-liners and "Want to help?" line are the owner-approved wording of
    the GitHub organisation profile (HeOCR/.github profile/README.md), so the site and GitHub say the same.
    """
    t = HOME[lang]
    tag = (f'<p class="he" lang="he" dir="rtl">{HOME["he"]["tagline"]}</p>' if lang == "en"
           else f'<p class="tag">{t["tagline"]}</p>')
    arrow = " ← " if lang == "he" else " → "
    flow = arrow.join(f'<span class="step">{step}</span>' for step in t["flow"])
    hero = (
        '<div class="home-hero band gridband">\n<div class="wrap">\n'
        f'{tag}\n<h1><span class="bb" data-tag="h1 · 0.99">HeOCR</span></h1>\n'
        f'<p class="lede">{html.escape(t["intro"])}</p>\n'
        '<div class="links">\n'
        f'      <a class="btn primary" href="download.html">{html.escape(t["download"])}</a>\n'
        f'      <a class="btn" href="benchmarks.html">{html.escape(t["bench"])}</a>\n'
        f'      <a class="btn" href="{ORG}">GitHub</a>\n'
        '    </div>\n'
        f'<div class="flow" aria-label="{t["flow_aria"]}">{flow}</div>\n'
        '</div>\n</div>\n'
    )
    text = re.sub(r'<div class="home-hero band gridband">.*?</div>\n</div>\n(?=<main)', lambda _: hero, text, count=1, flags=re.S)
    cards = "".join(
        f'      <div class="card">\n        <h3>{html.escape(title)}</h3>\n        <p>{html.escape(body)}</p>\n'
        f'        <p><a href="{href}">{html.escape(label)}</a></p>\n      </div>\n'
        for title, body, href, label in t["start_cards"]
    )
    start = (f'\n  <section id="start">\n    <h2>{html.escape(t["start"])}</h2>\n'
             f'    <div class="grid">\n{cards}    </div>\n  </section>\n')
    text = re.sub(r'(<main id="main" class="wrap home">\n)(?:\n  <section id="demo">.*?^  </section>\n)?'
                  r'(?:\n  <section id="start">.*?^  </section>\n)?',
                  lambda m: m[1] + demo_section(lang) + start, text, count=1, flags=re.M | re.S)
    groups = "".join(
        f'    <h3>{html.escape(group)}</h3>\n    <div class="grid">\n'
        + "".join(f'      <div class="card">\n        <h3><a href="{ORG}/{repo}">{repo}</a></h3>\n'
                  f'        <p>{html.escape(line)}</p>\n      </div>\n' for repo, line in repos)
        + '    </div>\n'
        for group, repos in t["groups"]
    )
    code = (f'  <section id="tools">\n    <h2>{html.escape(t["code"])}</h2>\n{groups}'
            f'    <p class="sub">{html.escape(t["help"])}</p>\n  </section>')
    return re.sub(r'^  <section id="tools">.*?^  </section>', lambda _: code, text, count=1, flags=re.M | re.S)


def block(name: str, body: str) -> str:
    return f"<!-- shell:{name} -->\n{body.rstrip()}\n<!-- /shell:{name} -->"


def render(page: str, lang: str, text: str) -> str:
    if page == "home":
        text = home_status(lang, text)
        text = home_layout(lang, text)
    title = re.search(r"<title>(.*?)</title>", text, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)">', text)
    desc = desc.group(1) if desc else None
    parts = {
        "head": shell.head_assets(lang, title, desc, page),
        "header": shell.header(lang, page),
        "partner": shell.partner(lang),
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
