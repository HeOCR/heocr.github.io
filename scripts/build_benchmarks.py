"""Build benchmarks.html and he/benchmarks.html from benchmarks/results.json.

    python3 scripts/build_benchmarks.py           # write both pages
    python3 scripts/build_benchmarks.py --check   # exit 1 if a committed page is out of date

Standard library only. The page styles are taken from rights.html and he/rights.html, so the benchmarks pages match
the rest of the site. Edit results.json (HeOCR's evaluation owner exports it after each scored run), then rebuild.
"""
from __future__ import annotations

import argparse, html, json, math, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402  (the site theme, one source for every page)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results.json"

EXTRA_CSS = """
  .bench section { max-width: none; }
  .bench h2 { margin-top: 0; }
  .bench h3 { font-size: 1.05rem; margin: 26px 0 4px; }
  .status { display: inline-block; background: var(--tag); color: var(--muted); padding: 2px 10px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin: 0 0 10px; }
  .empty { background: var(--surface); border: 1px dashed var(--line); border-radius: 12px; padding: 18px; color: var(--muted); }
  .tablewrap { overflow-x: auto; margin: 8px 0 6px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
  table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
  th, td { padding: 8px 12px; text-align: start; border-bottom: 1px solid var(--line); vertical-align: top; white-space: nowrap; }
  tr:last-child td { border-bottom: 0; }
  th { font-weight: 600; color: var(--muted); font-size: 0.82rem; }
  td.num { font-variant-numeric: tabular-nums; }
  .ci { display: block; color: var(--muted); font-size: 0.78rem; }
  tr.ours td { background: var(--accent-soft); }
  tr.ours td:first-child { font-weight: 600; }
  .facts { font-size: 0.85rem; color: var(--muted); margin: 6px 0 0; }
  .facts li { margin: 0 0 3px; }
  .warn { border-inline-start: 3px solid var(--accent); padding: 2px 0 2px 12px; padding-inline-start: 12px; margin: 10px 0; }
  .toc { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 8px; }
  .toc a { font-size: 0.9rem; }
  .hero { margin: 0; padding: 40px 0 8px; }
  .hero-axis, .hero-lane { display: grid; grid-template-columns: minmax(7rem, 15rem) 1fr 4.5rem; gap: 10px; align-items: center; }
  .hero-axis svg text { font-size: 11px; fill: var(--muted); }
  .hero-cell { padding: 8px 0; border-bottom: 1px solid var(--line); }
  .hero-name { font-weight: 600; font-size: 0.95rem; margin: 0 0 4px; }
  .hero-reader { font-size: 0.85rem; color: var(--muted); }
  .hero-lane.ours .hero-reader { color: var(--text); font-weight: 600; }
  .hero-val { font-size: 0.85rem; font-variant-numeric: tabular-nums; text-align: end; }
  .hero-ratio { font-size: 0.82rem; font-weight: 600; color: var(--accent); text-align: end; }
  .hero-missing { grid-column: 2 / 4; font-size: 0.82rem; color: var(--muted); font-style: italic; }
  .hero svg { direction: ltr; overflow: visible; }  /* the axis runs from 0% at the left on both pages; a dot at either end is drawn whole */
  .hero svg .track { stroke: var(--line); stroke-width: 2; }
  .hero svg .tick { stroke: var(--line); stroke-width: 1; }
  .hero svg .interval { stroke: var(--muted); stroke-width: 2; stroke-linecap: round; }
  .hero svg .dot { fill: var(--muted); stroke: var(--surface); stroke-width: 2; }
  .hero .ours svg .interval { stroke: var(--accent); }
  .hero .ours svg .dot { fill: var(--accent); }
  @media (max-width: 600px) {  /* a phone: each reader's name above its strip */
    .hero-axis, .hero-lane { grid-template-columns: 1fr 4rem; row-gap: 0; }
    .hero-axis > span:first-child { display: none; }
    .hero-reader { grid-column: 1 / -1; }
    .hero-missing { grid-column: 1 / -1; }
  }
"""

T = {
    "en": {
        "title": "HeOCR benchmarks",
        "desc": "How HeOCR's models and document reader compare with other open tools, per kind of Hebrew document.",
        "lede": "How HeOCR compares with other open tools, per kind of document. Every figure gives its sample size, a 95% interval, the measure, the reference and the run it comes from. The page is built from one file, <a href=\"{json}\">results.json</a>, which is updated after each scored run.",
        "back": "← HeOCR", "other": "עברית", "other_href": "he/benchmarks.html", "home": "./",
        "updated": "Updated {d}.",
        "lower": "lower is better", "higher": "higher is better",
        "no_data": "No data yet", "pending": "Pending",
        "pmod_h": "Modern printed Hebrew",
        "pmod_t": "No data yet — reference pages are under human review. No number is shown until a reviewed set is scored.",
        "phist_h": "Historical and rabbinic printed Hebrew",
        "phist_small": "This set is small: 38 pages from 14 books. Intervals are wide and most of them overlap, so treat differences between engines as indications, not rankings.",
        "hand_h": "Handwriting",
        "hand_t": "No data yet — there is no scored handwriting set with real, human-checked references.",
        "doc_h": "Documents by format",
        "doc_sub": "Generated documents with exact gold: Word files and PDFs of every kind HeOCR's document reader handles, made by our generators so the correct text is known exactly. Each table is one kind of document. heocr is developed against these sets, so they are not held out and flatter it; the release gate will score a fresh set made after its code is frozen. Release gate not yet run: these are measurements, not release verdicts.",
        "vend_h": "Commercial OCR vendors",
        "vend_t": "Scores pending human review of the reference pages.",
        "engine": "Engine", "reader": "Reader", "cer": "Character error (CER)", "wer": "Word error (WER)",
        "pages": "{p} pages, {c} books",
        "slice": {"all": "All 38 pages", "unpointed": "Without niqqud (pointed) pages", "rabbinic": "Rabbinic print, without niqqud",
                  "square": "Standard square type", "pointed": "Pointed text (niqqud) only"},
        "too_small": "Only 2 pages from 1 book: no interval, shown for completeness. Every engine fails here.",
        "not_scored": "{e} has not been scored on these pages.",
        "f_measure": "Measure", "f_ref": "Reference", "f_licence": "Licence", "f_interval": "Interval",
        "f_run": "Run", "f_code": "Scoring code", "f_readers": "Reader versions", "f_excluded": "Left out",
        "phist_run": "scored {d}; scorer {repo} at {commit}",
        "doc_run": "{run}; heocr at {commit}",
        "doc_code": "HeOCR's evaluation repository (not yet public; it is published with the release gate)",
        "doc_excluded": "two office-scan cases rendered with a proprietary font (their scores cannot be published), and the provisional section-number case from the label measure",
        "docs": "{n} documents",
        "na": "–",
        "cells": {"DOCX": "Word (.docx)", "DOC": "Legacy Word (.doc)", "PDF T1": "PDF with a correct text layer",
                  "PDF T2": "PDF whose text layer is in visual (reversed) order",
                  "PDF T3": "PDF with a broken but recoverable character map",
                  "PDF T4": "Scan with a wrong OCR text layer", "PDF T5": "Scan, image only",
                  "PDF T6": "Text layer plus text drawn as images", "PDF spread": "Two pages on one sheet",
                  "Scanned tables": "Scanned pages with a ruled table"},
        "m": {"cer": "Character error", "wer": "Word error", "number_recall": "Numbers found",
              "labels": "Section numbers correct", "rows_read": "Table rows read",
              "rows_silent": "Rows lost without a warning", "silent_loss": "Text lost without a warning",
              "image_word_recall": "Words in image regions found"},
        "readers": {"heocr": "heocr", "stock": "Tesseract (tessdata_best heb)", "docling": "Docling",
                    "markitdown": "MarkItDown", "pymupdf4llm": "PyMuPDF4LLM"},
        "reader_note": "Each table lists the readers that handle that format. Tesseract reads images only, so it appears on scans; on PDF T6 it is scored on the image regions only.",
        "cell_note": {"PDF T4": "T4 and T5 use the same scanned pages; heocr and Tesseract read both by OCR, so their figures match. T4 adds a wrong text layer, which the other readers use."},
        "wer_note": "Word error counts inserted words as well as wrong and missing ones, so it can exceed 100%.",
        "footer": "Created by <a href=\"http://www.shaypalachy.com/\">Shay Palachy Affek</a> and the HeOCR maintainers.",
        "hero_h": "Documents at a glance",
        "hero_measure": "Character error rate, lower is better. Dots are the run's values; bars are 95% intervals. One linear axis for every row, starting at 0%.",
        "hero_sets": "Generated documents with exact gold (D-bench). heocr is developed against these sets, so they are not held out.",
        "hero_run": "Run {run}, updated {d}. Release gate: {gate}.",
        "gate_not_run": "not yet run",
        "best_alt": "Best alternative: {name}",
        "no_alt": "No alternative reader was scored on this kind of document.",
        "no_score": "No character-error score in this run.",
        "of_docs": "{n} of {total} documents",
        "release_gate": "Release gate",
        "ratio": "{r}× fewer errors vs best alternative",
        "ratio_cap": "more than {r}× fewer errors vs best alternative",
    },
    "he": {
        "title": "מדדי ביצועים של HeOCR",
        "desc": "איך המודלים וקורא המסמכים של HeOCR משתווים לכלים פתוחים אחרים, לפי סוג המסמך העברי.",
        "lede": "איך HeOCR משתווה לכלים פתוחים אחרים, לפי סוג המסמך. לכל מספר מצוינים גודל המדגם, רווח בר־סמך של 95%, המדד, מקור הטקסט הנכון וההרצה שממנה הוא בא. הדף נבנה מקובץ אחד, <a href=\"{json}\">results.json</a>, שמתעדכן אחרי כל הרצה.",
        "back": "→ HeOCR", "other": "English", "other_href": "../benchmarks.html", "home": "./",
        "updated": "עודכן {d}.",
        "lower": "נמוך יותר עדיף", "higher": "גבוה יותר עדיף",
        "no_data": "אין עדיין נתונים", "pending": "ממתין",
        "pmod_h": "דפוס עברי מודרני",
        "pmod_t": "אין עדיין נתונים: דפי הייחוס נמצאים בבדיקה אנושית. לא יוצג מספר עד שתיבדק ותוערך קבוצה.",
        "phist_h": "דפוס עברי היסטורי ורבני",
        "phist_small": "הקבוצה קטנה: 38 עמודים מ־14 ספרים. רווחי הסמך רחבים ורובם חופפים, ולכן יש לקרוא את ההבדלים בין המנועים כסימנים, לא כדירוג.",
        "hand_h": "כתב יד",
        "hand_t": "אין עדיין נתונים: אין קבוצת כתב יד מוערכת עם טקסט ייחוס אמיתי שנבדק בידי אדם.",
        "doc_h": "מסמכים לפי פורמט",
        "doc_sub": "מסמכים מחוללים עם טקסט נכון מדויק: קובצי Word וקובצי PDF מכל הסוגים שקורא המסמכים של HeOCR מטפל בהם, שנוצרו במחוללים שלנו כך שהטקסט הנכון ידוע במדויק. כל טבלה היא סוג מסמך אחד. heocr מפותח מול הקבוצות האלה, ולכן הן אינן מוחזקות בצד ומחמיאות לו; שער השחרור יעריך קבוצה חדשה שתיווצר אחרי שהקוד יוקפא. שער השחרור עוד לא הורץ: אלה מדידות, לא החלטות שחרור.",
        "vend_h": "ספקי OCR מסחריים",
        "vend_t": "הציונים ממתינים לבדיקה אנושית של דפי הייחוס.",
        "engine": "מנוע", "reader": "קורא", "cer": "שגיאת תווים (CER)", "wer": "שגיאת מילים (WER)",
        "pages": "{p} עמודים, {c} ספרים",
        "slice": {"all": "כל 38 העמודים", "unpointed": "בלי עמודים מנוקדים", "rabbinic": "דפוס רבני, בלי ניקוד",
                  "square": "אותיות מרובעות רגילות", "pointed": "טקסט מנוקד בלבד"},
        "too_small": "רק 2 עמודים מספר אחד: בלי רווח סמך, מוצג לשלמות התמונה. כל המנועים נכשלים כאן.",
        "not_scored": "{e} עוד לא הוערך על העמודים האלה.",
        "f_measure": "מדד", "f_ref": "טקסט ייחוס", "f_licence": "רישיון", "f_interval": "רווח סמך",
        "f_run": "הרצה", "f_code": "קוד ההערכה", "f_readers": "גרסאות הקוראים", "f_excluded": "הושמטו",
        "phist_run": "הוערך ב־{d}; כלי ההערכה {repo} בגרסה {commit}",
        "doc_run": "{run}; heocr בגרסה {commit}",
        "doc_code": "מאגר ההערכה של HeOCR (עדיין לא פומבי; יפורסם עם שער השחרור)",
        "doc_excluded": "שני מקרים של סריקות משרדיות שנוצרו בגופן קנייני (אי אפשר לפרסם את הציונים שלהם), ומקרה מספור הסעיפים הזמני ממדד מספרי הסעיפים",
        "docs": "{n} מסמכים",
        "na": "–",
        "cells": {"DOCX": "Word ‏(‎.docx‏)", "DOC": "Word ישן ‏(‎.doc‏)", "PDF T1": "PDF עם שכבת טקסט תקינה",
                  "PDF T2": "PDF ששכבת הטקסט שלו בסדר חזותי (הפוך)",
                  "PDF T3": "PDF עם מפת תווים שבורה אך ניתנת לשחזור",
                  "PDF T4": "סריקה עם שכבת OCR שגויה", "PDF T5": "סריקה, תמונה בלבד",
                  "PDF T6": "שכבת טקסט ועוד טקסט שמצויר כתמונה", "PDF spread": "שני עמודים בגיליון אחד",
                  "Scanned tables": "עמודים סרוקים עם טבלה"},
        "m": {"cer": "שגיאת תווים", "wer": "שגיאת מילים", "number_recall": "מספרים שנמצאו",
              "labels": "מספרי סעיפים נכונים", "rows_read": "שורות טבלה שנקראו",
              "rows_silent": "שורות שאבדו בלי אזהרה", "silent_loss": "טקסט שאבד בלי אזהרה",
              "image_word_recall": "מילים שנמצאו באזורי תמונה"},
        "readers": {"heocr": "heocr", "stock": "Tesseract ‏(tessdata_best heb)", "docling": "Docling",
                    "markitdown": "MarkItDown", "pymupdf4llm": "PyMuPDF4LLM"},
        "reader_note": "בכל טבלה מופיעים הקוראים שמטפלים בפורמט שלה. Tesseract קורא תמונות בלבד, ולכן הוא מופיע בסריקות; ב־PDF T6 הוא מוערך על אזורי התמונה בלבד.",
        "x_phist_set": "audit2: ‏38 עמודים מוגהים מ־14 ספרים בוויקיטקסט העברי, עם טקסט ייחוס שנבדק בידי אדם",
        "x_phist_measure": "hocrgen evaluate-references, פרופיל primary.v1 (טקסט העמוד, יחס של סכומים על פני העמודים)",
        "x_phist_interval": "bootstrap של 95% באשכולות לפי ספר בוויקיטקסט (2000 דגימות, seed 20261106); בלי רווח סמך מתחת ל־3 ספרים",
        "x_doc_interval": "bootstrap של 95% על פני המסמכים (2000 דגימות, seed 0)",
        "x_doc_ref": "קבוצות D-bench מחוללות A, B ו־C: מסמכים שנוצרו עם טקסט נכון מדויק; הטקסט מתוך רשומות (העיתון הרשמי), נחלת הכלל",
        "x_ws": "ויקיטקסט העברי",
        "cell_note": {"PDF T4": "T4 ו־T5 משתמשים באותם עמודים סרוקים; heocr ו־Tesseract קוראים את שניהם ב־OCR, ולכן התוצאות שלהם זהות. ב־T4 נוספת שכבת טקסט שגויה, שבה משתמשים הקוראים האחרים."},
        "wer_note": "שגיאת מילים סופרת גם מילים שנוספו, לא רק מילים שגויות או חסרות, ולכן היא יכולה לעלות על 100%.",
        "footer": "נוצר בידי <a href=\"http://www.shaypalachy.com/\">שי פלצ'י אפק</a> ומתחזקי HeOCR.",
        "hero_h": "המסמכים במבט אחד",
        "hero_measure": "שיעור שגיאת התווים, נמוך יותר עדיף. הנקודות הן הערכים בהרצה; הקווים הם רווחי סמך של 95%. ציר ליניארי אחד לכל השורות, שמתחיל ב־0%.",
        "hero_sets": "מסמכים מחוללים עם טקסט נכון מדויק (D-bench). heocr מפותח מול הקבוצות האלה, ולכן הן אינן מוחזקות בצד.",
        "hero_run": "הרצה {run}, עודכן {d}. שער השחרור: {gate}.",
        "gate_not_run": "עוד לא הורץ",
        "best_alt": "החלופה הטובה ביותר: {name}",
        "no_alt": "אף קורא חלופי לא הוערך על סוג המסמך הזה.",
        "no_score": "אין ציון שגיאת תווים בהרצה הזו.",
        "of_docs": "{n} מתוך {total} מסמכים",
        "release_gate": "שער השחרור",
        "ratio": "פי {r} פחות שגיאות מהחלופה הטובה ביותר",
        "ratio_cap": "יותר מפי {r} פחות שגיאות מהחלופה הטובה ביותר",
    },
}
LOWER = {"cer", "wer", "rows_silent", "silent_loss"}
READER_ORDER = ["heocr", "stock", "docling", "markitdown", "pymupdf4llm"]
CELL_MEASURES = {"DOCX": ["cer", "wer", "number_recall", "labels"], "DOC": ["cer", "wer", "number_recall"],
                 "Scanned tables": ["rows_read", "rows_silent", "cer", "number_recall"],
                 "PDF T6": ["cer", "wer", "number_recall", "silent_loss", "image_word_recall"]}
PDF_MEASURES = ["cer", "wer", "number_recall", "silent_loss"]
e = html.escape


def pct(x):
    if x is None:
        return "–"
    v = 100 * x
    return f"{v:.2f}%" if abs(v) < 1 else f"{v:.1f}%"


def cell_html(v, ci):
    if v is None:
        return '<td class="num">–</td>'
    s = f'<bdi dir="ltr">{pct(v)}</bdi>'
    if ci:
        s += f'<span class="ci"><bdi dir="ltr">[{pct(ci[0]).rstrip("%")}–{pct(ci[1])}]</bdi></span>'
    return f'<td class="num">{s}</td>'


ALTERNATIVES = ["docling", "markitdown", "pymupdf4llm"]  # the open alternatives; stock Tesseract is shown on its own lane
HERO_MEASURE = "cer"


def hero_series(R: dict) -> dict:
    """The hero chart's data, from results.json alone: per documents cell, in the file's order, three lanes,
    heocr, the best alternative (the lowest character error rate among ALTERNATIVES) and stock Tesseract
    (tessdata_best heb, always shown). A lane holds the CER and its 95% interval, or None when the reader
    has no score in the cell. Only readers present in results.json appear. ``axis`` is the one linear
    axis every row shares: from 0 to the largest interval end, rounded up to a clean tick (``hero_axis``)."""
    D = R["documents"]
    cells = []

    def lane(key, role, rec, documents):
        m = (rec or {}).get(HERO_MEASURE)
        if not m:
            return {"key": key, "role": role, "value": None}
        lo, hi = m["ci95"] if m.get("ci95") else (m["value"], m["value"])
        return {"key": key, "role": role, "value": m["value"], "lo": lo, "hi": hi,
                "n": m.get("n", rec.get("documents")), "documents": documents}

    for cell, c in D["cells"].items():
        readers = c["readers"]
        alts = [(readers[k][HERO_MEASURE]["value"], k) for k in ALTERNATIVES if HERO_MEASURE in readers.get(k, {})]
        best = min(alts)[1] if alts else None  # ties go to the earlier name in ALTERNATIVES order, deterministically
        lanes = [
            lane("heocr", "ours", readers.get("heocr"), c["documents"]),
            lane(best, "alt", readers.get(best) if best else None, c["documents"]),
            lane("stock", "stock", readers.get("stock"), c["documents"]),
        ]
        cells.append({"cell": cell, "documents": c["documents"], "lanes": lanes, "ratio": hero_ratio(lanes[0], lanes[1])})
    top = max((ln["hi"] for c in cells for ln in c["lanes"] if ln["value"] is not None), default=0.0)
    return {"measure": HERO_MEASURE, "cells": cells, "axis": hero_axis(top), "run": D["run"], "updated": R["updated"],
            "gate": D.get("gate", "not_run")}


HERO_RATIO_CAP = 50  # above it, "more than 50x": a point value near zero makes a huge ratio unstable


def hero_ratio(ours: dict, alt: dict) -> dict | None:
    """How many times fewer errors heocr makes than the best alternative, from the two point estimates; only
    when the two 95% intervals do not overlap and heocr's is the lower, else None (and None with no alternative).
    ``text`` is the figure: an integer from 3x, one decimal below, and the cap (``capped``) above HERO_RATIO_CAP."""
    if ours["value"] is None or alt["value"] is None or not ours["hi"] < alt["lo"]:
        return None
    r = alt["value"] / ours["value"] if ours["value"] > 0 else math.inf
    if r > HERO_RATIO_CAP:
        return {"value": r, "text": str(HERO_RATIO_CAP), "capped": True}
    return {"value": r, "text": f"{r:.0f}" if r >= 3 else f"{r:.1f}", "capped": False}


HERO_TICK_STEPS = (0.01, 0.02, 0.025, 0.05, 0.1, 0.2, 0.25, 0.5)  # error rates; the smallest giving at most 5 intervals


def hero_axis(top: float) -> dict:
    """The shared linear axis: 0 to ``top`` rounded up to a clean tick, at most 5 intervals."""
    step = next((s for s in HERO_TICK_STEPS if math.ceil(round(top / s, 9)) <= 5), 1.0)
    n = max(1, math.ceil(round(top / step, 9)))
    return {"max": round(n * step, 4), "ticks": [round(i * step, 4) for i in range(n + 1)]}


def hero_html(H: dict, t: dict, lang: str) -> str:
    """Draw the hero chart: plain HTML rows with one small inline SVG strip per lane (the shared 0-to-max track, the
    interval as a line, the value as a dot). All colour comes from the page's CSS variables, so it reads in
    both themes, and all drawing is here, apart from the data (hero_series)."""
    out = [f'<figure class="hero" aria-labelledby="hero-h">\n<h2 id="hero-h">{e(t["hero_h"])}</h2>\n'
           f'<p class="sub">{e(t["hero_measure"])}</p>\n']
    top = H["axis"]["max"]
    at = lambda v: round(100 * max(0.0, min(top, v)) / top, 2)  # position in the strip, %
    ticks = "".join(f'<line x1="{at(v)}%" x2="{at(v)}%" y1="0" y2="16" class="tick"/>' for v in H["axis"]["ticks"])
    last = len(H["axis"]["ticks"]) - 1
    labels = "".join(f'<text x="{at(v)}%" y="12" text-anchor="{"start" if i == 0 else "end" if i == last else "middle"}">{100 * v:g}%</text>'
                     for i, v in enumerate(H["axis"]["ticks"]))
    out.append(f'<div class="hero-axis"><span></span><svg dir="ltr" width="100%" height="16" aria-hidden="true">{labels}</svg><span></span></div>\n')
    d = "rtl" if lang == "he" else "ltr"
    for c in H["cells"]:
        out.append(f'<div class="hero-cell">\n<div class="hero-name"><bdi dir="{d}">{e(t["cells"][c["cell"]])}</bdi> <span class="note">· <bdi dir="ltr">{c["cell"]}</bdi> · '
                   f'<bdi dir="{d}">{e(t["docs"].format(n=c["documents"]))}</bdi></span></div>\n')
        for ln in c["lanes"]:
            if ln["role"] == "alt":
                name = t["best_alt"].format(name=t["readers"][ln["key"]]) if ln["key"] else t["readers"].get("alt", "")
            else:
                name = t["readers"][ln["key"]]
            if ln["value"] is None:
                msg = t["no_alt"] if ln["role"] == "alt" and not ln["key"] else t["no_score"]
                out.append(f'<div class="hero-lane {ln["role"]} none"><span class="hero-reader">{e(name) if ln["key"] else ""}</span>'
                           f'<span class="hero-missing">{e(msg)}</span></div>\n')
                continue
            sub = ""
            if ln["n"] is not None and ln["n"] != ln["documents"]:
                sub = f' <span class="ci">{e(t["of_docs"].format(n=ln["n"], total=ln["documents"]))}</span>'
            x, lo, hi = (at(v) for v in (ln["value"], ln["lo"], ln["hi"]))
            tip = f'{name}: {pct(ln["value"])} [{pct(ln["lo"])}–{pct(ln["hi"])}]'
            out.append(f'<div class="hero-lane {ln["role"]}"><span class="hero-reader">{e(name)}{sub}</span>'
                       f'<svg dir="ltr" width="100%" height="16" role="img" aria-label="{e(tip)}">{ticks}'
                       f'<line x1="0%" x2="100%" y1="8" y2="8" class="track"/>'
                       f'<line x1="{lo}%" x2="{hi}%" y1="8" y2="8" class="interval"/>'
                       f'<circle cx="{x}%" cy="8" r="5" class="dot"><title>{e(tip)}</title></circle></svg>'
                       f'<span class="hero-val"><bdi dir="ltr">{pct(ln["value"])}</bdi></span></div>\n')
            if ln["role"] == "ours" and c["ratio"]:
                r = c["ratio"]
                out.append(f'<div class="hero-ratio">{e(t["ratio_cap" if r["capped"] else "ratio"].format(r=r["text"]))}</div>\n')
        out.append("</div>\n")
    gate = t["gate_not_run"] if H["gate"] == "not_run" else H["gate"]
    out.append(f'<figcaption class="note">{e(t["hero_sets"])} {e(t["hero_run"].format(run=H["run"], d=H["updated"], gate=gate))}</figcaption>\n</figure>\n')
    return "".join(out)


def facts(rows):
    return '<ul class="facts">' + "".join(f"<li><strong>{e(k)}:</strong> {v}</li>" for k, v in rows) + "</ul>"


def page(lang: str, R: dict) -> str:
    t = T[lang]
    style_src = (ROOT / ("he/rights.html" if lang == "he" else "rights.html")).read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", style_src, re.S).group(1)
    pre = "../" if lang == "he" else ""
    json_href = f"{pre}benchmarks/results.json"
    P, D = R["p_hist"], R["documents"]
    out = []
    w = out.append
    # --- head
    w(f'<!doctype html>\n<html lang="{lang}"{" dir=\"rtl\"" if lang == "he" else ""}>\n<head>\n<meta charset="utf-8">\n{theme.HEAD}'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{e(t["title"])}</title>\n<meta name="description" content="{e(t["desc"])}">\n')
    fonts = ("family=Frank+Ruhl+Libre:wght@500;700&family=Heebo:wght@400;500;600&family=Inter:wght@400;500;600"
             if lang == "he" else "family=Frank+Ruhl+Libre:wght@500;700&family=Inter:wght@400;500;600")
    w('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
      f'<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">\n')
    w(f"<style>{style}{EXTRA_CSS}</style>\n")
    w('<link rel="alternate" hreflang="en" href="https://heocr.github.io/benchmarks.html">\n'
      '<link rel="alternate" hreflang="he" href="https://heocr.github.io/he/benchmarks.html">\n</head>\n<body>\n\n')
    # --- header
    cur = '<span aria-current="page" lang="{0}">{1}</span>'.format(lang, "עברית" if lang == "he" else "English")
    oth = f'<a href="{t["other_href"]}" lang="{"en" if lang == "he" else "he"}" hreflang="{"en" if lang == "he" else "he"}">{t["other"]}</a>'
    w(f'<header>\n  <div class="wrap">\n    <nav class="langbar" aria-label="{"שפה / Language" if lang == "he" else "Language / שפה"}">\n'
      f'      <div class="lang-toggle">\n        {cur}\n        {oth}\n      </div>\n      {theme.button(lang)}\n    </nav>\n'
      f'    <a class="back" href="{t["home"]}">{t["back"]}</a>\n    <h1>{e(t["title"])}</h1>\n'
      f'    <p class="lede">{t["lede"].format(json=json_href)}</p>\n'
      f'    <p class="note">{e(t["updated"].format(d=R["updated"]))}</p>\n  </div>\n</header>\n\n')
    w('<main class="wrap doc bench">\n')
    w(hero_html(hero_series(R), t, lang))
    w(f'<!-- release-gate: eval adds the "{e(t["release_gate"])}" section here after the gate verdict -->\n<div id="release-gate"></div>\n')
    ids = [("p-mod", t["pmod_h"]), ("p-hist", t["phist_h"]), ("handwriting", t["hand_h"]),
           ("documents", t["doc_h"]), ("vendors", t["vend_h"])]
    w('<nav class="toc">' + " · ".join(f'<a href="#{i}">{e(h)}</a>' for i, h in ids) + "</nav>\n")
    # --- 1. P-mod
    w(f'<section id="p-mod">\n<h2>{e(t["pmod_h"])}</h2>\n<span class="status">{e(t["no_data"])}</span>\n'
      f'<div class="empty">{e(t["pmod_t"])}</div>\n</section>\n')
    # --- 2. P-hist
    w(f'<section id="p-hist">\n<h2>{e(t["phist_h"])}</h2>\n<p class="warn">{e(t["phist_small"])}</p>\n')
    for s in P["slices"]:
        w(f'<h3>{e(t["slice"][s["id"]])} <span class="note">· {e(t["pages"].format(p=s["pages"], c=s["clusters"]))}</span></h3>\n')
        if s["too_small"]:
            w(f'<p class="note">{e(t["too_small"])}</p>\n')
        w(f'<div class="tablewrap"><table>\n<thead><tr><th>{e(t["engine"])}</th><th>{e(t["cer"])} <span class="ci">{e(t["lower"])}</span></th>'
          f'<th>{e(t["wer"])} <span class="ci">{e(t["lower"])}</span></th></tr></thead>\n<tbody>\n')
        for k, row in s["engines"].items():
            meta = P["engines"][k]
            name = e(meta["name"])
            if meta.get("url"):
                name = f'<a href="{e(meta["url"])}">{name}</a>'
            w(f'<tr{" class=\"ours\"" if meta["ours"] else ""}><td>{name}</td>{cell_html(row["cer"], row["cer_ci95"])}'
              f'{cell_html(row["wer"], row["wer_ci95"])}</tr>\n')
        w("</tbody></table></div>\n")
    ref = P["reference"]
    w(facts([
        (t["f_measure"], e(t.get("x_phist_measure", P["measure"]))),
        (t["f_ref"], f'{e(t.get("x_phist_set", P["set"]))}; <a href="{e(ref["source_url"])}">{e(t.get("x_ws", ref["source"]))}</a> (<code>{e(ref["name"])}</code>)'),
        (t["f_licence"], e(ref["licence"])),
        (t["f_interval"], e(t.get("x_phist_interval", P["interval"]))),
        (t["f_run"], e(t["phist_run"].format(d=P["scored"], repo=P["scorer"]["repo"], commit=P["scorer"]["commit"]))),
        (t["f_code"], f'<a href="{e(P["scorer"]["url"])}">{e(P["scorer"]["repo"])}</a> <code>evaluate-references</code>'),
    ]))
    for x in P.get("not_scored", []):
        w(f'<p class="note">{e(t["not_scored"].format(e=x))}</p>\n')
    w("</section>\n")
    # --- 3. Handwriting
    w(f'<section id="handwriting">\n<h2>{e(t["hand_h"])}</h2>\n<span class="status">{e(t["no_data"])}</span>\n'
      f'<div class="empty">{e(t["hand_t"])}</div>\n</section>\n')
    # --- 4. Documents
    w(f'<section id="documents">\n<h2>{e(t["doc_h"])}</h2>\n<p class="sub">{e(t["doc_sub"])}</p>\n')
    for cell, c in D["cells"].items():
        ms = CELL_MEASURES.get(cell, PDF_MEASURES)
        w(f'<h3>{e(t["cells"][cell])} <span class="note">· {cell} · {e(t["docs"].format(n=c["documents"]))}</span></h3>\n')
        w(f'<div class="tablewrap"><table>\n<thead><tr><th>{e(t["reader"])}</th>' +
          "".join(f'<th>{e(t["m"][m])} <span class="ci">{e(t["lower"] if m in LOWER else t["higher"])}</span></th>' for m in ms) +
          "</tr></thead>\n<tbody>\n")
        for r in READER_ORDER:
            x = c["readers"].get(r)
            if not x or not any(m in x for m in ms):
                continue  # the reader does not handle this format
            tds = "".join(cell_html(x[m]["value"], x[m]["ci95"]) if x and m in x else '<td class="num">–</td>' for m in ms)
            w(f'<tr{" class=\"ours\"" if r == "heocr" else ""}><td>{e(t["readers"][r])}</td>{tds}</tr>\n')
        w("</tbody></table></div>\n")
        if cell in t["cell_note"]:
            w(f'<p class="note">{e(t["cell_note"][cell])}</p>\n')
    commit = re.search(r"[0-9a-f]{40}", D["heocr"])
    commit = commit.group(0)[:7] if commit else D["heocr"]
    ref = D["reference"]
    vers = "; ".join(f'{e(t["readers"][k])} {e(v.get("version") or v.get("ocr", ""))}' for k, v in D["baselines"].items())
    w(f'<p class="note">{e(t["reader_note"])}</p>\n')
    w(f'<p class="note">{e(t["wer_note"])}</p>\n')
    w(facts([
        (t["f_measure"], f'<code>{e(D["measure"])}</code> (text normalised the same way for every reader; ratios of sums over documents)'
         if lang == "en" else f'<code>{e(D["measure"])}</code> (הטקסט מנורמל באותו אופן לכל הקוראים; יחס של סכומים על פני המסמכים)'),
        (t["f_ref"], e(t.get("x_doc_ref", f'{ref["name"]}: {ref["source"]}'))),
        (t["f_licence"], e(ref["licence"])),
        (t["f_interval"], e(t.get("x_doc_interval", D["interval"]))),
        (t["f_run"], e(t["doc_run"].format(run=D["run"], commit=commit))),
        (t["f_readers"], vers),
        (t["f_excluded"], e(t["doc_excluded"])),
        (t["f_code"], e(t["doc_code"])),
    ]))
    w("</section>\n")
    # --- 5. Vendors
    w(f'<section id="vendors">\n<h2>{e(t["vend_h"])}</h2>\n<span class="status">{e(t["pending"])}</span>\n'
      f'<div class="empty">{e(t["vend_t"])}</div>\n</section>\n')
    w("</main>\n\n<footer>\n  <div class=\"wrap\">\n"
      f'    <p>{t["footer"]}</p>\n    <p><a href="{json_href}">results.json</a> · <a href="{t["home"]}">HeOCR</a></p>\n'
      "  </div>\n</footer>\n\n" + theme.BODY + "</body>\n</html>\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    R = json.loads(RESULTS.read_text(encoding="utf-8"))
    stale = []
    for lang, path in (("en", ROOT / "benchmarks.html"), ("he", ROOT / "he" / "benchmarks.html")):
        s = page(lang, R)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_benchmarks.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
