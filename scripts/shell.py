"""The site shell, one source for every page: head, header, footer, page head, page index.

The "Bounding Box" brand (design/brand-handover/). Styles are site.css and theme.js at the site root,
used as delivered; nothing here writes CSS. The generated pages (benchmarks, htext) call these
functions; the hand-written pages (index, rights) carry the same blocks, kept in sync by
scripts/apply_shell.py between ``<!-- shell:… -->`` markers.

- Light is the default whatever the OS setting; night mode only through the toggle, remembered in
  localStorage under ``heocr-theme`` (theme.js). The one-line head script applies a saved night choice
  before the first paint, so it never flashes light.
- Hebrew is the default language and lives at the site root; English lives under ``en/``. English pages differ
  from Hebrew only by ``lang="en" dir="ltr"``, the strings below, and ``../`` before assets.
"""
from __future__ import annotations

from html import escape as e

SITE = "https://heocr.org"
STORAGE_KEY = "heocr-theme"
TAG_H1 = "h1 · 0.99"
FONTS = ("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700"
         "&amp;family=Noto+Sans+Hebrew:wght@400;500;700;800&amp;display=swap")

# page key -> file name, relative to the language's directory (Hebrew: the site root; English: en/)
PAGES = {
    "home": "index.html",
    "bench": "benchmarks.html",
    "htext": "htext.html",
    "rights": "rights.html",
    "download": "download.html",
    "datasets": "datasets.html",
    "privacy": "privacy.html",  # linked from the Download page, not in the header
}
LINKED_PAGES = PAGES | {"methodology": "methodology.html", "leaderboard": "leaderboard.html"}
LANG_DIR = {"he": "", "en": "en/"}  # Hebrew is the default language: the root
LANGS = ("he", "en")


def site_path(lang: str, page: str) -> str:
    """Path of ``page`` in ``lang`` relative to the site root, e.g. ``en/htext.html``."""
    return LANG_DIR[lang] + LINKED_PAGES[page]


NAV = ("download", "bench", "datasets", "htext", "rights")  # site review 2, ARCH-01

STR = {
    "en": {
        "nav": {"download": "Download", "bench": "Benchmarks", "datasets": "Datasets", "htext": "Text corpora",
                "rights": "Rights &amp; takedown"},
        "nav_aria": "Site", "lang_aria": "Language / שפה", "theme": "Night mode",
        "skip": "Skip to content", "toc_aria": "On this page", "lang_name": "English",
    },
    "he": {
        "nav": {"download": "הורדה", "bench": "מדדי ביצועים", "datasets": "מאגרי נתונים", "htext": "מאגרי טקסט",
                "rights": "זכויות והסרה"},
        "nav_aria": "ניווט באתר", "lang_aria": "שפה / Language", "theme": "מצב לילה",
        "skip": "דילוג לתוכן", "toc_aria": "בעמוד זה", "lang_name": "עברית",
    },
}

MARK = ('<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="7" y="7" width="34" height="34" class="lg-box sw2"></rect>'
        '<rect x="4" y="4" width="6" height="6" class="lg-h"></rect><rect x="38" y="4" width="6" height="6" class="lg-h"></rect>'
        '<rect x="4" y="38" width="6" height="6" class="lg-h"></rect><rect x="38" y="38" width="6" height="6" class="lg-h"></rect>'
        '<path d="M16 18H32V32.5" class="lg-ink sw45"></path><path d="M16 24.5V32.5" class="lg-ink sw45"></path></svg>')
ICONS = ('<svg class="ico i-moon" viewBox="0 0 16 16" aria-hidden="true"><path d="M13 9.6A5.6 5.6 0 0 1 6.4 3 5.6 5.6 0 1 0 13 9.6z"></path></svg>'
         '<svg class="ico i-sun" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3"></circle>'
         '<path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"></path></svg>')


def prefix(lang: str) -> str:
    """What to put before a site-root asset (site.css, theme.js, ...) on a page in ``lang``."""
    return "../" if LANG_DIR[lang] else ""


def _rel(lang: str, target_lang: str, page: str) -> str:
    """Link from a page in ``lang`` to ``page`` in ``target_lang``."""
    name = LINKED_PAGES[page]
    if name == "index.html":
        name = ""
    if lang == target_lang:
        return name or "./"
    return prefix(lang) + LANG_DIR[target_lang] + name or "./"


def page_url(lang: str, page: str) -> str:
    """Absolute URL of ``page`` in ``lang`` (an index page is its directory)."""
    return f"{SITE}/{site_path(lang, page)}".replace("index.html", "")


def head_assets(lang: str, title: str, desc: str | None, page: str) -> str:
    """Everything in <head> after the title: fonts, stylesheet, theme script, icons, link previews."""
    p = prefix(lang)
    url = page_url(lang, page)
    out = [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link href="{FONTS}" rel="stylesheet">',
        f'<link rel="stylesheet" href="{p}site.css">',
        f'<script>(function(){{try{{if(localStorage.getItem("{STORAGE_KEY}")==="dark")document.documentElement.dataset.theme="dark"}}catch(e){{}}}})()</script>',
        f'<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{p}favicon.ico" sizes="48x48">',
        f'<link rel="apple-touch-icon" href="{p}apple-touch-icon.png">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="HeOCR">',
        f'<meta property="og:title" content="{title}">',
    ]
    if desc:
        out.append(f'<meta property="og:description" content="{desc}">')
    out += [
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SITE}/og-image-{lang}-1200x630.png">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<link rel="canonical" href="{url}">',
        f'<link rel="alternate" hreflang="he" href="{page_url("he", page)}">',
        f'<link rel="alternate" hreflang="en" href="{page_url("en", page)}">',
        f'<link rel="alternate" hreflang="x-default" href="{page_url("he", page)}">',
    ]
    return "\n".join(out)


def head(lang: str, title: str, desc: str | None, page: str) -> str:
    """The document start, through <body>: for the generated pages."""
    meta = f'\n<meta name="description" content="{desc}">' if desc else ""
    return (f'<!doctype html>\n<html lang="{lang}" dir="{"rtl" if lang == "he" else "ltr"}">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{title}</title>{meta}\n'
            f'{head_assets(lang, title, desc, page)}\n</head>\n<body class="site">\n')


def header(lang: str, page: str) -> str:
    t = STR[lang]
    other = "he" if lang == "en" else "en"
    nav = "".join(f'<a href="{_rel(lang, lang, k)}"{" aria-current=\"page\"" if k == page else ""}>{t["nav"][k]}</a>' for k in NAV)
    return (f'<a class="skip" href="#main">{t["skip"]}</a>\n<header class="site-header">\n<div class="wrap bar">\n'
            f'<a class="brand" href="{_rel(lang, lang, "home")}" aria-label="HeOCR">{MARK}<span dir="ltr">He<b>OCR</b></span></a>\n'
            f'<nav class="site-nav" aria-label="{t["nav_aria"]}">{nav}</nav>\n<div class="tools">\n'
            f'<div class="lang-toggle" role="group" aria-label="{t["lang_aria"]}">\n'
            f'<span aria-current="page" lang="{lang}">{t["lang_name"]}</span>\n'
            f'        <a href="{_rel(lang, other, page)}" lang="{other}" hreflang="{other}">{STR[other]["lang_name"]}</a>\n</div>\n'
            f'<button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false">{ICONS}<span class="label">{t["theme"]}</span></button>\n'
            '</div>\n</div>\n</header>\n')


def footer(lines: list[str]) -> str:
    """The footer: the brand, then the page's own lines (each a ready <p>…</p>)."""
    return ('<footer class="site-footer">\n<div class="wrap foot">\n<div class="foot-brand">He<b>OCR</b></div>\n'
            '<div class="foot-text">\n' + "\n".join(lines) + '\n</div>\n</div>\n</footer>\n')


def tail(lang: str) -> str:
    return f'<script src="{prefix(lang)}theme.js"></script>\n</body>\n</html>\n'


def boxed(inner_html: str) -> str:
    """The page title in its detection box."""
    return f'<span class="bb" data-tag="{TAG_H1}">{inner_html}</span>'


def page_head(title_html: str, rest_html: str) -> str:
    """The page head on its grid band: the boxed h1, then the lede and notes."""
    return f'<div class="band gridband"><div class="wrap page-head">\n<h1>{boxed(title_html)}</h1>\n{rest_html}\n</div></div>\n'


def toc(lang: str, links: list[tuple[str, str, str | None]]) -> str:
    """The page index: one link per section, with an optional status under it."""
    items = "".join(f'<a href="#{i}">{name}{f"<small>{small}</small>" if small else ""}</a>' for i, name, small in links)
    return f'<nav class="wrap" aria-label="{STR[lang]["toc_aria"]}"><div class="toc">{items}</div></nav>\n'


__all__ = ["e", "head", "head_assets", "header", "footer", "tail", "boxed", "page_head", "toc", "prefix", "STR", "PAGES"]
