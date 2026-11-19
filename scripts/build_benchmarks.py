"""Build benchmarks.html and he/benchmarks.html from benchmarks/results.json.

    python3 scripts/build_benchmarks.py           # write both pages
    python3 scripts/build_benchmarks.py --check   # exit 1 if a committed page is out of date

Standard library only. The markup follows the "Bounding Box" design (design/brand-handover/site/benchmarks.html);
styles are site.css, the shell is scripts/shell.py, and the hero chart is scripts/hero_chart.py (the handover's,
unchanged). Every number comes from results.json (HeOCR's evaluation owner exports it after each scored run).
"""
from __future__ import annotations

import argparse, html, json, math, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hero_chart as hc  # noqa: E402  (the hero chart, from the brand handover)
import shell  # noqa: E402  (head, header, footer: one source for every page)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results.json"

T = {
    "en": {
        "title": "HeOCR benchmarks",
        "desc": "How HeOCR's models and document reader compare with other open tools, per kind of Hebrew document.",
        "lede": "How HeOCR compares with other open tools, per kind of document. Every figure gives its sample size, a 95% interval, the measure, the reference and the run it comes from. The page is built from one file, <a href=\"{json}\">results.json</a>, which is updated after each scored run.",
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
        "release_gate": "Release gate",
    },
    "he": {
        "title": "מדדי ביצועים של HeOCR",
        "desc": "איך המודלים וקורא המסמכים של HeOCR משתווים לכלים פתוחים אחרים, לפי סוג המסמך העברי.",
        "lede": "איך HeOCR משתווה לכלים פתוחים אחרים, לפי סוג המסמך. לכל מספר מצוינים גודל המדגם, רווח בר־סמך של 95%, המדד, מקור הטקסט הנכון וההרצה שממנה הוא בא. הדף נבנה מקובץ אחד, <a href=\"{json}\">results.json</a>, שמתעדכן אחרי כל הרצה.",
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
        "release_gate": "שער השחרור",
    },
}

# Strings new with the "Bounding Box" design (design/brand-handover/site/MARKUP.md, "New wording"): listed in the
# redesign PR for the maintainers to edit freely. The Hebrew needs a native read.
NEW = {
    "en": {
        "kicker": "Documents by format", "chart_title": "Character error by document type", "ours": "ours",
        "lg_alt": "Best other open tool", "lg_alt_s": "the lowest of Docling, MarkItDown and PyMuPDF4LLM",
        "lg_tess": "Stock Tesseract", "lg_tess_s": "heb, tessdata_best",
        "run": "Run", "gate_not_run": "not run", "gate_run": "run",
        "axis_note": "One linear axis from 0 to 100%; bars start at zero. Whiskers show the interval ({interval}). "
                     "Where an interval is narrower than its marker, read it from the numbers beside it.",
        "more": "Documents by format: every reader and every measure",
        "scored": "Scored",
        "gate_sub": "The release gate scores a fresh set, made after the code is frozen. "
                    "Each document type then gets one verdict: supported, or not supported.",
        "gate_count": "<strong>{d}</strong> of {n} document types have a verdict",
        "v_supported": "Supported", "v_unsupported": "Not supported", "v_pending": "Awaiting run",
        "method": "Method, reference and run",
        "cell_note_legend": "A dash means the reader has no score on that measure. An empty cell means the measure does not apply to that document type. The last column holds a measure that exists for one type only; its name is in that type's heading row.",
        "caveat_from": "heocr is developed", "fixed_from": "Release gate not yet run",
        "doc_sub_run": "It has since run, on heocr {version}: the verdicts come from that fresh set, while the figures in these tables are the earlier development run.",
        "gate_ran": "Run {name}: heocr {version} (commit {commit}), scored {date}. The verdict is set by the one-sided 97.5% upper bound of heocr's difference from each other reader, against a fixed margin.",
        "gate_hero": "{s} of {n} supported",
        "not_measured": "Not measured on a held-out set yet",
        "phist_nm": "Not measured on a held-out set yet. The historical-print test set is waiting for volunteer references; no figure is shown until it is scored.",
        "doc_sub_heldout": "Generated documents with exact gold: Word files and PDFs of every kind HeOCR's document reader handles, made by our generators so the correct text is known exactly. Each table is one kind of document. These figures come from the release gate's fresh set: generated with new seeds after heocr {version}'s code was frozen, so heocr was never tuned on these documents. They are drawn by the same generators heocr is developed against, so a good figure means good on generated documents of this kind, not more.",
        "doc_caveat_heldout": "Held-out set: the release gate's fresh generated documents, made after heocr {version}'s code was frozen.",
        "why_cmp": "vs {reader}: {measure}, difference {delta}, upper bound {upper} &gt; margin {margin} points",
        "why_veto": {"reversed_amounts": "held back by the real-document check: reversed amounts"},
        "why_m": {"number_recall": "Numbers missed", "image_word_recall": "Words in image regions missed", "rows_read": "Table rows not read"},
    },
    "he": {
        "kicker": "מסמכים לפי פורמט", "chart_title": "שגיאת תווים לפי סוג מסמך", "ours": "שלנו",
        "lg_alt": "הכלי הפתוח האחר הטוב ביותר", "lg_alt_s": "הנמוך ביותר מבין Docling,‏ MarkItDown ו־PyMuPDF4LLM",
        "lg_tess": "Tesseract הרגיל", "lg_tess_s": "heb, tessdata_best",
        "run": "הרצה", "gate_not_run": "עוד לא הורץ", "gate_run": "הורץ",
        "axis_note": "ציר ליניארי אחד, מ־0 עד 100%; הפסים מתחילים באפס. הקווים עם הקצוות מסמנים את רווח הסמך ({interval}). "
                     "כשהרווח צר מהסמן, הוא מופיע במספרים שלצידו.",
        "more": "מסמכים לפי פורמט: כל הקוראים וכל המדדים",
        "scored": "הוערך",
        "gate_sub": "שער השחרור מעריך קבוצה חדשה, שנוצרת אחרי שהקוד מוקפא. "
                    "לכל סוג מסמך ניתנת אז החלטה אחת: נתמך או לא נתמך.",
        "gate_count": "ל־<strong>{d}</strong> מתוך {n} סוגי מסמכים יש החלטה",
        "v_supported": "נתמך", "v_unsupported": "לא נתמך", "v_pending": "ממתין להרצה",
        "method": "שיטה, טקסט ייחוס והרצה",
        "cell_note_legend": "קו מפריד פירושו שלקורא אין ציון במדד הזה. תא ריק פירושו שהמדד אינו חל על סוג המסמך הזה. בעמודה האחרונה מופיע מדד שקיים רק לסוג מסמך אחד; שמו מופיע בשורת הכותרת של אותו סוג.",
        "caveat_from": "heocr מפותח", "fixed_from": "שער השחרור עוד לא הורץ",
        "doc_sub_run": "מאז הוא הורץ, על heocr {version}: ההחלטות מבוססות על הקבוצה החדשה הזו, והמספרים בטבלאות האלה הם מהרצת הפיתוח הקודמת.",
        "gate_ran": "הרצה {name}: heocr {version} (קומיט {commit}), הוערכה ב־{date}. ההחלטה נקבעת לפי הגבול העליון החד־צדדי ברמת 97.5% של ההפרש בין heocr לכל קורא אחר, מול סף קבוע.",
        "gate_hero": "{s} מתוך {n} נתמכים",
        "not_measured": "עוד לא נמדד על קבוצה מוחזקת בצד",
        "phist_nm": "עוד לא נמדד על קבוצה מוחזקת בצד. קבוצת המבחן של הדפוס ההיסטורי ממתינה לטקסטי ייחוס ממתנדבים; לא יוצג מספר עד שהיא תוערך.",
        "doc_sub_heldout": "מסמכים מחוללים עם טקסט נכון מדויק: קובצי Word וקובצי PDF מכל הסוגים שקורא המסמכים של HeOCR מטפל בהם, שנוצרו במחוללים שלנו כך שהטקסט הנכון ידוע במדויק. כל טבלה היא סוג מסמך אחד. המספרים האלה הם מהקבוצה החדשה של שער השחרור: נוצרה עם seeds חדשים אחרי שהקוד של heocr {version} הוקפא, ולכן heocr מעולם לא כוונן עליה. היא נוצרה באותם מחוללים ש־heocr מפותח מולם, ולכן מספר טוב פירושו טוב על מסמכים מחוללים מהסוג הזה, לא יותר.",
        "doc_caveat_heldout": "קבוצה מוחזקת בצד: המסמכים המחוללים החדשים של שער השחרור, שנוצרו אחרי שהקוד של heocr {version} הוקפא.",
        "why_cmp": "מול {reader}: {measure}, הפרש {delta}, גבול עליון {upper} &gt; סף {margin} נקודות",
        "why_veto": {"reversed_amounts": "נעצר בבדיקת המסמכים האמיתיים: סכומים הפוכים"},
        "why_m": {"number_recall": "מספרים שהוחמצו", "image_word_recall": "מילים שהוחמצו באזורי תמונה", "rows_read": "שורות טבלה שלא נקראו"},
    },
}
for _lang in T:
    T[_lang].update(NEW[_lang])

READER_ORDER = ["heocr", "stock", "docling", "markitdown", "pymupdf4llm"]
STD = ("cer", "wer", "number_recall", "labels", "silent_loss", "image_word_recall")  # text formats, in column order
TBL = ("rows_read", "rows_silent", "cer", "number_recall")                            # scanned tables
EXTRA = ("labels", "image_word_recall")  # measures that exist for one type only: the shared last column
UP = {"number_recall", "labels", "image_word_recall", "rows_read"}                     # higher is better
VERDICTS = {"supported": "supported", "not_supported": "unsupported", "unsupported": "unsupported"}
ICON = {
    "info": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6"></circle><path d="M8 7.3v3.5M8 5.1v.1"></path></svg>',
    "supported": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.6l3 3 6-7.2"></path></svg>',
    "unsupported": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"></path></svg>',
    "partial": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.6"></circle><path d="M8 2.4v11.2"></path></svg>',
    "pending": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.6"></circle><path d="M8 4.9V8l2 1.3"></path></svg>',
}
NA = '<td class="num na">–</td>'
e = html.escape


def cell_html(v, ci):
    if v is None:
        return NA
    civ = f'<span class="ci"><bdi dir="ltr">{hc.interval(ci)}%</bdi></span>' if ci else ""
    return f'<td class="num"><span class="v"><bdi dir="ltr">{hc.pct(v)}</bdi></span>{civ}</td>'


def verdict(kind, t, lg=False, label=None):
    return f'<span class="verdict {kind}{" lg" if lg else ""}">{ICON[kind]}{label or t["v_" + kind]}</span>'


def cell_verdicts(D) -> dict:
    """{cell: 'supported' | 'unsupported'} from results.json, once eval adds verdicts after the gate."""
    return {c: VERDICTS[v["verdict"]] for c, v in D["cells"].items() if v.get("verdict") in VERDICTS}


def present(cell) -> set:
    return set().union(*[set(r) - {"documents"} for r in cell["readers"].values()])


def col_head(t, m):
    return f'{e(t["m"][m])}<span class="dir{" up" if m in UP else ""}">{e(t["higher"] if m in UP else t["lower"])}</span>'


def slug(code):
    return "doc-" + code.lower().replace(" ", "-")


def docs_tables(t, D, verdicts):
    """Two grouped tables: the text formats and the scanned tables, one <tbody> per document type."""
    out = []
    cells = D["cells"]
    for order, pick in ((STD, lambda c: "rows_read" not in present(c)), (TBL, lambda c: "rows_read" in present(c))):
        group = {c: v for c, v in cells.items() if pick(v)}
        if not group:
            continue
        cols = [m for m in order if m not in EXTRA and any(m in present(v) for v in group.values())]
        has_extra = any(m in present(v) for v in group.values() for m in EXTRA)
        head = [f'<th scope="col">{e(t["reader"])}</th>'] + [f'<th scope="col">{col_head(t, m)}</th>' for m in cols]
        if has_extra:
            head.append('<td class="thx"></td>')
        out.append(f'<div class="tablewrap"><table>\n<thead><tr>{"".join(head)}</tr></thead>')
        for code, cell in group.items():
            mine = present(cell)
            extra = next((m for m in EXTRA if m in mine), None)
            badge = verdict(verdicts[code], t) if code in verdicts else ""
            gnote = f'<span class="gnote">{e(t["cell_note"][code])}</span>' if code in t["cell_note"] else ""
            colh = ""
            if extra:
                ns = {r[extra]["n"] for r in cell["readers"].values() if extra in r and "n" in r[extra]}
                ntag = f'<span class="tag-n">n = {min(ns)}</span>' if len(ns) == 1 and ns != {cell["documents"]} else ""
                colh = f'<th class="colh" scope="col">{col_head(t, extra).replace("</span>", ntag + "</span>")}</th>'
            span = len(cols) + 1 + (1 if has_extra and not extra else 0)
            meta = f'· {code} · {e(t["docs"].format(n=cell["documents"]))}'
            out.append(f'<tbody>\n<tr class="group"><th colspan="{span}" scope="rowgroup" id="{slug(code)}">'
                       f'<span class="gtitle">{e(t["cells"][code])} <span class="note">{meta}</span>{badge}{gnote}</span></th>{colh}</tr>')
            for key in READER_ORDER:
                if key not in cell["readers"]:
                    continue
                r = cell["readers"][key]
                ours = key == "heocr"
                label = e(t["readers"][key]) + (f'<span class="tag-ours">{e(t["ours"])}</span>' if ours else "")
                if r.get("documents", cell["documents"]) != cell["documents"]:
                    label += f'<span class="tag-n block">n = {r["documents"]}</span>'
                tds = []
                for m in cols + ([extra] if extra else [None] if has_extra else []):
                    if m is None or m not in mine:
                        tds.append('<td class="nap"></td>')
                    elif m not in r:
                        tds.append(NA)
                    else:
                        tds.append(cell_html(r[m]["value"], r[m]["ci95"]))
                out.append(f'<tr{" class=\"ours\"" if ours else ""}><td>{label}</td>{"".join(tds)}</tr>')
            out.append("</tbody>")
        out.append("</table></div>")
    return "\n".join(out)


def hist_table(t, P):
    head = (f'<th scope="col">{e(t["engine"])}</th><th scope="col">{e(t["cer"])}<span class="dir">{e(t["lower"])}</span></th>'
            f'<th scope="col">{e(t["wer"])}<span class="dir">{e(t["lower"])}</span></th>')
    out = [f'<div class="tablewrap narrow"><table>\n<thead><tr>{head}</tr></thead>']
    for s in P["slices"]:
        meta = f'· {e(t["pages"].format(p=s["pages"], c=s["clusters"]))}'
        gnote = f'<span class="gnote">{e(t["too_small"])}</span>' if s["too_small"] else ""
        out.append(f'<tbody>\n<tr class="group"><th colspan="3" scope="rowgroup"><span class="gtitle">{e(t["slice"][s["id"]])} '
                   f'<span class="note">{meta}</span>{gnote}</span></th></tr>')
        for k, row in s["engines"].items():
            meta_e = P["engines"][k]
            name = e(meta_e["name"])
            if meta_e.get("url"):
                name = f'<a href="{e(meta_e["url"])}">{name}</a>'
            if meta_e["ours"]:
                name += f'<span class="tag-ours">{e(t["ours"])}</span>'
            out.append(f'<tr{" class=\"ours\"" if meta_e["ours"] else ""}><td>{name}</td>'
                       f'{cell_html(row["cer"], row["cer_ci95"])}{cell_html(row["wer"], row["wer_ci95"])}</tr>')
        out.append("</tbody>")
    out.append("</table></div>")
    return "\n".join(out)


def facts(rows):
    return '<ul class="facts">' + "".join(f"<li><strong>{e(k)}:</strong> {v}</li>" for k, v in rows) + "</ul>"


def method(t, rows):
    return f'<details class="method"><summary>{e(t["method"])}</summary>\n{facts(rows)}\n</details>'


def domain_head(h2, status, cls=""):
    return f'<div class="domain-head"><h2>{h2}</h2><span class="status{cls}">{status}</span></div>'


def legend(t):
    return ('<ul class="hc-legend">\n'
            f'<li class="ours">{hc.legend_marker("ours")}<span><b>heocr</b> <small>{e(t["ours"])}</small></span></li>\n'
            f'<li>{hc.legend_marker("alt")}<span><b>{e(t["lg_alt"])}</b> <small>{e(t["lg_alt_s"])}</small></span></li>\n'
            f'<li>{hc.legend_marker("tess")}<span><b>{e(t["lg_tess"])}</b> <small>{e(t["lg_tess_s"])}</small></span></li>\n'
            "</ul>")


def hero_badge(t, D, not_run, gate):
    if not_run:
        return verdict("pending", t, label=t["release_gate"] + ": " + gate)
    v = [c.get("verdict") for c in D["cells"].values()]
    s = v.count("supported")
    kind = "supported" if s == len(v) else "unsupported" if s == 0 else "partial"
    return verdict(kind, t, label=t["release_gate"] + ": " + t["gate_hero"].format(s=s, n=len(v)))


def hero(t, lang, R, doc_interval):
    D = R["documents"]
    not_run = D.get("gate", "not_run") == "not_run"
    gate = t["gate_not_run"] if not_run else t["gate_run"]
    sub = doc_sub(t, D, not_run)
    caveat = (t["doc_caveat_heldout"].format(version=D["gate_run"]["heocr"]) if D.get("heldout")
              else sub[sub.index(t["caveat_from"]):])
    svgs = hc.hero_svg(D, lang, "wide") + "\n" + hc.hero_svg(D, lang, "narrow")
    return f'''<figure class="wrap hero-chart" id="hero">
<div class="panel" data-tag="figure · hero">
<p class="kicker">{e(t["kicker"])}</p>
<div class="hc-title"><h2>{e(t["chart_title"])}</h2><span class="dir">{e(t["lower"])}</span></div>
<p class="hc-finding">{hc.finding_sentence(D, lang)}</p>
{legend(t)}
{svgs}
<figcaption class="hc-foot">
<p class="hc-run"><span>{e(t["run"])} <code>{e(D["run"])}</code></span><span><bdi dir="ltr">{e(R["updated"])}</bdi></span>{hero_badge(t, D, not_run, gate)}</p>
<p class="note">{e(caveat)}</p>
<p class="note">{e(t["axis_note"].format(interval=doc_interval))}</p>
<p class="note"><a href="#documents">{e(t["more"])}</a></p>
</figcaption>
</div>
</figure>
'''


def num(x):
    return f'<bdi dir="ltr">{x:.2f}</bdi>'.replace("-", "\u2212")


def why(t, cell):
    """The failed comparisons of a not-supported type, from results.json's gate_failed."""
    out = []
    for f in cell.get("gate_failed", []):
        if "veto" in f:
            out.append(e(t["why_veto"][f["veto"]]))
        else:
            out.append(t["why_cmp"].format(reader=e(hc.READER_NAMES.get(f["baseline"], f["baseline"])), measure=e(t["why_m"].get(f["measure"], t["m"][f["measure"]])),
                                           delta=num(f["delta"]), upper=num(f["upper_97_5"]), margin=num(f["margin"])))
    return f'<span class="why">{"; ".join(out)}</span>' if out else ""


def gate_block(t, lang, D, verdicts):
    kinds = [verdicts.get(c, "pending") for c in D["cells"]]
    strip = "".join(f'<span class="gate-cell {k}">{"" if k == "pending" else ICON[k]}</span>' for k in kinds)
    decided = sum(k != "pending" for k in kinds)
    if decided == len(kinds):
        count = (f'<strong>{kinds.count("supported")}</strong>{e(t["v_supported"])}<span class="sep">·</span>'
                 f'<strong>{kinds.count("unsupported")}</strong>{e(t["v_unsupported"])}')
    else:
        count = t["gate_count"].format(d=decided, n=len(kinds))
    items = "".join(f'<li><a href="#{slug(c)}"><span class="code">{c}</span> <span class="name">{e(hc.TYPE_LABELS[lang][c])}</span>{why(t, D["cells"][c])}</a>'
                    f'{verdict(k, t)}</li>\n' for c, k in zip(D["cells"], kinds))
    return (f'<div class="gate-summary">\n<div class="gate-strip" aria-hidden="true">{strip}</div>\n<p class="gate-count">{count}</p>\n</div>\n'
            f'<ul class="gate-list">\n{items}</ul>')


def gate_ran(t, D):
    g = D["gate_run"]
    return t["gate_ran"].format(name=g["name"], version=g["heocr"], commit=g["commit"][:7], date=g["scored"])


def doc_sub(t, D, not_run):
    if D.get("heldout"):
        return t["doc_sub_heldout"].format(version=D["gate_run"]["heocr"])
    if not_run:
        return t["doc_sub"]
    return t["doc_sub"][:t["doc_sub"].index(t["fixed_from"])] + t["doc_sub_run"].format(version=D["gate_run"]["heocr"])


def cap(s):
    return s[:1].upper() + s[1:]


def page(lang: str, R: dict) -> str:
    t = T[lang]
    pre = shell.prefix(lang)
    json_href = f"{pre}benchmarks/results.json"
    P, D = R["p_hist"], R["documents"]
    verdicts = cell_verdicts(D)
    not_run = D.get("gate", "not_run") == "not_run"
    gate_state = cap(t["gate_not_run"] if not_run else t["gate_run"])
    doc_interval = t.get("x_doc_interval", D["interval"])
    w = []
    w.append(shell.head(lang, e(t["title"]), e(t["desc"]), "bench"))
    w.append(shell.header(lang, "bench"))
    w.append('<main id="main" class="bench">\n')
    w.append(shell.page_head(e(t["title"]), f'<p class="lede">{t["lede"].format(json=json_href)}</p>\n'
                                             f'<p class="note">{e(t["updated"].format(d=R["updated"]))}</p>'))
    w.append(hero(t, lang, R, doc_interval))
    p_nm = P.get("status") == "not_measured"
    sections = [("p-mod", t["pmod_h"], t["no_data"], ""),
                ("p-hist", t["phist_h"], t["not_measured"] if p_nm else t["scored"], "" if p_nm else " scored"),
                ("handwriting", t["hand_h"], t["no_data"], ""), ("documents", t["doc_h"], t["scored"], " scored"),
                ("vendors", t["vend_h"], t["pending"], "")]
    w.append(shell.toc(lang, [(i, e(h), e(st)) for i, h, st, _ in sections] + [("gate", e(t["release_gate"]), e(gate_state))]))

    w.append(empty("p-mod", t["pmod_h"], t["no_data"], t["pmod_t"]))
    # --- historical print: one grouped table, once a held-out set is scored
    if p_nm:
        w.append(empty("p-hist", t["phist_h"], t["not_measured"], t["phist_nm"]))
    else:
        w.append(phist_section(t, P))
    w.append(empty("handwriting", t["hand_h"], t["no_data"], t["hand_t"]))
    w.extend(rest_of_page(t, lang, R, D, verdicts, not_run, gate_state, doc_interval, json_href))
    return "".join(w)


def phist_section(t, P):
    w = []
    ref = P["reference"]
    w.append(f'<section id="p-hist" class="wrap domain">\n'
             f'{domain_head(e(t["phist_h"]), e(t["scored"]) + " <bdi dir=\"ltr\">" + e(P["scored"]) + "</bdi>", " scored")}\n'
             f'<p class="warn">{ICON["info"]}<span>{e(t["phist_small"])}</span></p>\n{hist_table(t, P)}\n')
    w.append(method(t, [
        (t["f_measure"], e(t.get("x_phist_measure", P["measure"]))),
        (t["f_ref"], f'{e(t.get("x_phist_set", P["set"]))}; <a href="{e(ref["source_url"])}">{e(t.get("x_ws", ref["source"]))}</a> (<code>{e(ref["name"])}</code>)'),
        (t["f_licence"], e(ref["licence"])),
        (t["f_interval"], e(t.get("x_phist_interval", P["interval"]))),
        (t["f_run"], e(t["phist_run"].format(d=P["scored"], repo=P["scorer"]["repo"], commit=P["scorer"]["commit"]))),
        (t["f_code"], f'<a href="{e(P["scorer"]["url"])}">{e(P["scorer"]["repo"])}</a> <code>evaluate-references</code>'),
    ]) + "\n")
    for x in P.get("not_scored", []):
        w.append(f'<p class="note">{e(t["not_scored"].format(e=x))}</p>\n')
    w.append("</section>\n")
    return "".join(w)


def empty(sid, h2, status, text):
    return (f'<section id="{sid}" class="wrap domain">\n{domain_head(e(h2), e(status))}\n'
            f'<div class="empty">{e(text)}</div>\n</section>\n')


def rest_of_page(t, lang, R, D, verdicts, not_run, gate_state, doc_interval, json_href):
    w = []
    # --- documents by format: two grouped tables
    commit = re.search(r"[0-9a-f]{40}", D["heocr"])
    commit = commit.group(0)[:7] if commit else D["heocr"]
    dref = D["reference"]
    vers = "; ".join(f'{e(t["readers"][k])} {e(v.get("version") or v.get("ocr", ""))}' for k, v in D["baselines"].items())
    w.append(f'<section id="documents" class="wrap domain">\n'
             f'{domain_head(e(t["doc_h"]), e(t["scored"]) + " <bdi dir=\"ltr\">" + e(R["updated"]) + "</bdi>", " scored")}\n'
             f'<p class="sub">{e(doc_sub(t, D, not_run))}</p>\n{docs_tables(t, D, verdicts)}\n'
             f'<p class="legend-note">{e(t["cell_note_legend"])}</p>\n'
             f'<p class="note">{e(t["reader_note"])}</p>\n<p class="note">{e(t["wer_note"])}</p>\n')
    w.append(method(t, [
        (t["f_measure"], f'<code>{e(D["measure"])}</code> (text normalised the same way for every reader; ratios of sums over documents)'
         if lang == "en" else f'<code>{e(D["measure"])}</code> (הטקסט מנורמל באותו אופן לכל הקוראים; יחס של סכומים על פני המסמכים)'),
        (t["f_ref"], e(t.get("x_doc_ref", f'{dref["name"]}: {dref["source"]}'))),
        (t["f_licence"], e(dref["licence"])),
        (t["f_interval"], e(doc_interval)),
        (t["f_run"], e(t["doc_run"].format(run=D["run"], commit=commit))),
        (t["f_readers"], vers),
        (t["f_excluded"], e(t["doc_excluded"])),
        (t["f_code"], e(t["doc_code"])),
    ]) + "\n</section>\n")
    w.append(empty("vendors", t["vend_h"], t["pending"], t["vend_t"]))
    # --- release gate
    fixed = t["doc_sub"][t["doc_sub"].index(t["fixed_from"]):] if not_run else ""
    pend = verdict("pending", t, label=gate_state) if not_run else ""
    w.append(f'<section id="gate" class="wrap domain">\n<div class="domain-head"><h2>{e(t["release_gate"])}</h2>{pend}</div>\n'
             f'<p class="sub">{e(t["gate_sub"])}{" " + e(fixed) if fixed else ""}{" " + e(gate_ran(t, D)) if not not_run else ""}</p>\n{gate_block(t, lang, D, verdicts)}\n</section>\n')
    w.append("</main>\n")
    w.append(shell.footer([f"<p>{t['footer']}</p>", f'<p><a href="{json_href}">results.json</a> · <a href="./">HeOCR</a></p>']))
    w.append(shell.tail(lang))
    return w


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
