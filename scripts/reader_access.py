"""How each benchmark reader can be obtained: open (open source or open weights, runs locally), paid (hosted
service billed per use) or free_closed (hosted at no charge, code and weights not published).

Classification is by reader name and fails closed: an unknown reader returns None, and the page builders refuse
to write a page that contains one (see check_classified)."""
from __future__ import annotations

import re

RULES = (
    (r"^HeOCR\b", "open"),
    (r"^(Tesseract|Tessdata)\b", "open"),
    (r"^Rivok\b", "open"),
    (r"^Kraken\b", "open"),
    (r"^PaddleOCR\b", "open"),
    (r"^Qwen", "open"),
    (r"^Google Drive\b", "free_closed"),
    (r"^(Google|Gemini|Claude)\b", "paid"),
)
KINDS = ("open", "free_closed", "paid")
LABEL = {
    "en": {"open": "Open", "free_closed": "Free, closed", "paid": "Paid"},
    "he": {"open": "פתוח", "free_closed": "חינמי, סגור", "paid": "בתשלום"},
}
LEGEND = {
    "en": {
        "title": "Reader access",
        "open": "open-source code or open weights that run locally at no cost.",
        "free_closed": "a hosted service available at no charge; code and weights are not published.",
        "paid": "a hosted cloud service billed per use.",
        "best": "best score in the column (lowest error, or highest mark recall).",
        "best_open": "best score among open readers, where that is not also the best overall.",
    },
    "he": {
        "title": "סוגי מנועים",
        "open": "קוד פתוח או משקולות פתוחות, שאפשר להריץ באופן מקומי ללא תשלום.",
        "free_closed": "שירות מקוון ללא תשלום. הקוד והמשקולות אינם מפורסמים.",
        "paid": "שירות ענן מקוון בתשלום לפי שימוש.",
        "best": "התוצאה הטובה ביותר בעמודה (שיעור השגיאות הנמוך ביותר, או זיהוי הניקוד הגבוה ביותר).",
        "best_open": "התוצאה הטובה ביותר בין המנועים הפתוחים, כשהיא אינה גם הטובה ביותר בעמודה.",
    },
}
BEST_OPEN = {"en": "Lowest error among open readers", "he": "שיעור השגיאות הנמוך ביותר בין המנועים הפתוחים"}
BEST_OPEN_HIGH = {"en": "Highest among open readers", "he": "השיעור הגבוה ביותר בין המנועים הפתוחים"}
SWATCH = {"en": ("Best", "Best open"), "he": ("הטוב ביותר", "הטוב בין הפתוחים")}


def classify(name):
    for pattern, kind in RULES:
        if re.match(pattern, name):
            return kind
    return None


def badge(name, lang):
    kind = classify(name)
    if kind is None:
        return '<span class="reader-access" data-access="unknown"></span>'
    return (f'<span class="reader-access reader-access-{kind.replace("_", "-")}" data-access="{kind}">'
            f'{LABEL[lang][kind]}</span>')


def legend(lang, *, highlights=True):
    t = LEGEND[lang]
    items = [f'<li><span class="reader-access reader-access-{k.replace("_", "-")}">{LABEL[lang][k]}</span> {t[k]}</li>'
             for k in KINDS]
    if highlights:
        items.append(f'<li><span class="benchmark-best">{SWATCH[lang][0]}</span> {t["best"]}</li>')
        items.append(f'<li><span class="benchmark-best-open">{SWATCH[lang][1]}</span> {t["best_open"]}</li>')
    return (f'<div class="reader-access-legend"><p class="reader-access-legend-title">{t["title"]}</p>'
            f'<ul>{"".join(items)}</ul></div>')


def check_classified(html_text):
    if 'data-access="unknown"' in html_text:
        raise ValueError("A benchmark reader has no access classification; add it to reader_access.RULES")
