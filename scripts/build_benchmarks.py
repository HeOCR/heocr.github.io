"""Generate the English and Hebrew benchmark status reports from the public results file."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import shell

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results.json"

T = {
    "en": {
        "title": 'HeOCR benchmarks',
        "desc": 'How HeOCR reads real Hebrew pages, next to other open tools: figures from real-world held-out sets only.',
        "lede": 'How HeOCR reads real Hebrew pages, next to other open tools. Every figure gives its sample size, a 95% interval, the measure, the reference and the run it comes from. The page is built from one file, <a href="{json}">results.json</a>, which is updated after each scored run.',
        "updated": 'Updated {d}.',
        "lower": 'lower is better',
        "pmod_h": 'Modern printed Hebrew',
        "phist_h": 'Historical and rabbinic printed Hebrew',
        "phist_small": 'This set is small: 38 pages from 14 books. Intervals are wide and most of them overlap, so treat differences between engines as indications, not rankings.',
        "hand_h": 'Handwriting',
        "hand_t": 'No data yet — there is no scored handwriting set with real, human-checked references.',
        "hw_sub": "225 handwritten Hebrew lines by 10 writers, photographed by phone, from ivrit.ai's Hebrew handwriting OCR benchmark (test split). Held out: no HeOCR model was trained, tuned or chosen on them. Each reader gets each line image as it is.",
        "hw_finding": "Handwriting is not supported yet. On these held-out lines every reader, ours included, gets most characters wrong. HeOCR's own model, trained on print, does worse here than stock Tesseract's model ({d} points of character error, 95% interval {lo} to {hi}).",
        "hw_caveat": "No HeOCR model is trained on handwriting. The reference text is ivrit.ai's volunteer transcription, not checked by us. With 10 writers, intervals are wide. Word error can pass 100% when a reader writes more wrong words than the line has.",
        "hw_cols": ('Character error', 'Word error', 'Words found'),
        "hw_readers": {'heocr': 'heocr, one-line mode (heocr_modern_v1)', 'heocr_psm3': 'heocr (heocr_modern_v1, PSM 3)', 'heocr_stockheb': "heocr with stock Tesseract's model", 'stock_best': 'Tesseract (tessdata_best heb)', 'stock_fast': 'Tesseract (tessdata_fast heb)'},
        "hw_credit": 'Data: {name} (<a href="{url}">Hugging Face</a>), from <a href="{corpus}">transcriptor.ivrit.ai</a>; {licence}.',
        "engine": 'Engine',
        "cer": 'Character error (CER)',
        "wer": 'Word error (WER)',
        "pages": '{p} pages, {c} books',
        "slice": {'all': 'All 38 pages', 'unpointed': 'Without niqqud (pointed) pages', 'rabbinic': 'Rabbinic print, without niqqud', 'square': 'Standard square type', 'pointed': 'Pointed text (niqqud) only'},
        "too_small": 'Only 2 pages from 1 book: no interval, shown for completeness. Every engine fails here.',
        "not_scored": '{e} has not been scored on these pages.',
        "f_measure": 'Measure',
        "f_ref": 'Reference',
        "f_licence": 'Licence',
        "f_interval": 'Interval',
        "f_run": 'Run',
        "f_code": 'Scoring code',
        "phist_run": 'scored {d}; scorer {repo} at {commit}',
        "ours": 'ours',
        "scored": 'Scored',
        "method": 'Method, reference and run',
        "not_measured": 'Not measured on a held-out set yet',
        "phist_nm": 'Not measured on a held-out set yet. The historical-print test set is waiting for volunteer references; no figure is shown until it is scored.',
        "release_note": 'We will release models or a pipeline version once we outperform existing readers on at least one document type.',
    },
    "he": {
        "title": 'מדדי ביצועים של HeOCR',
        "desc": 'איך HeOCR קורא דפים עבריים אמיתיים, לצד כלים פתוחים אחרים: מספרים מקבוצות אמיתיות שהוחזקו בצד בלבד.',
        "lede": 'איך HeOCR קורא דפים עבריים אמיתיים, לצד כלים פתוחים אחרים. לכל מספר מצוינים גודל המדגם, רווח בר־סמך של 95%, המדד, מקור הטקסט הנכון וההרצה שממנה הוא בא. הדף נבנה מקובץ אחד, <a href="{json}">results.json</a>, שמתעדכן אחרי כל הרצה.',
        "updated": 'עודכן {d}.',
        "lower": 'נמוך יותר עדיף',
        "pmod_h": 'דפוס עברי מודרני',
        "phist_h": 'דפוס עברי היסטורי ורבני',
        "phist_small": 'הקבוצה קטנה: 38 עמודים מ־14 ספרים. רווחי הסמך רחבים ורובם חופפים, ולכן יש לקרוא את ההבדלים בין המנועים כסימנים, לא כדירוג.',
        "hand_h": 'כתב יד',
        "hand_t": 'אין עדיין נתונים: אין קבוצת כתב יד מוערכת עם טקסט ייחוס אמיתי שנבדק בידי אדם.',
        "hw_sub": '225 שורות בכתב יד עברי של 10 כותבים, שצולמו בטלפון, ממבחן זיהוי כתב היד העברי של ivrit.ai (חלק המבחן). מוחזקות בצד: אף מודל של HeOCR לא אומן, כוונן או נבחר עליהן. כל קורא מקבל את תמונת השורה כפי שהיא.',
        "hw_finding": 'כתב יד עדיין אינו נתמך. בשורות המוחזקות בצד האלה כל הקוראים, גם שלנו, טועים ברוב התווים. המודל של HeOCR, שאומן על דפוס, גרוע כאן מהמודל הרגיל של Tesseract ({d} נקודות של שגיאת תווים, רווח סמך 95% מ־{lo} עד {hi}).',
        "hw_caveat": 'אף מודל של HeOCR לא אומן על כתב יד. טקסט הייחוס הוא התעתוק של מתנדבי ivrit.ai, ולא נבדק בידינו. עם 10 כותבים רווחי הסמך רחבים. שגיאת המילים יכולה לעבור 100% כשקורא כותב יותר מילים שגויות ממספר המילים בשורה.',
        "hw_cols": ('שגיאת תווים', 'שגיאת מילים', 'מילים שנמצאו'),
        "hw_readers": {'heocr': 'heocr, מצב שורה אחת (heocr_modern_v1)', 'heocr_psm3': 'heocr (heocr_modern_v1, PSM 3)', 'heocr_stockheb': 'heocr עם המודל הרגיל של Tesseract', 'stock_best': 'Tesseract (tessdata_best heb)', 'stock_fast': 'Tesseract (tessdata_fast heb)'},
        "hw_credit": 'נתונים: {name} (<a href="{url}">Hugging Face</a>), מתוך <a href="{corpus}">transcriptor.ivrit.ai</a>; {licence}.',
        "engine": 'מנוע',
        "cer": 'שגיאת תווים (CER)',
        "wer": 'שגיאת מילים (WER)',
        "pages": '{p} עמודים, {c} ספרים',
        "slice": {'all': 'כל 38 העמודים', 'unpointed': 'בלי עמודים מנוקדים', 'rabbinic': 'דפוס רבני, בלי ניקוד', 'square': 'אותיות מרובעות רגילות', 'pointed': 'טקסט מנוקד בלבד'},
        "too_small": 'רק 2 עמודים מספר אחד: בלי רווח סמך, מוצג לשלמות התמונה. כל המנועים נכשלים כאן.',
        "not_scored": '{e} עוד לא הוערך על העמודים האלה.',
        "f_measure": 'מדד',
        "f_ref": 'טקסט ייחוס',
        "f_licence": 'רישיון',
        "f_interval": 'רווח סמך',
        "f_run": 'הרצה',
        "f_code": 'קוד ההערכה',
        "phist_run": 'הוערך ב־{d}; כלי ההערכה {repo} בגרסה {commit}',
        "x_phist_set": 'audit2: \u200f38 עמודים מוגהים מ־14 ספרים בוויקיטקסט העברי, עם טקסט ייחוס שנבדק בידי אדם',
        "x_phist_measure": 'hocrgen evaluate-references, פרופיל primary.v1 (טקסט העמוד, יחס של סכומים על פני העמודים)',
        "x_phist_interval": 'bootstrap של 95% באשכולות לפי ספר בוויקיטקסט (2000 דגימות, seed 20261106); בלי רווח סמך מתחת ל־3 ספרים',
        "x_ws": 'ויקיטקסט העברי',
        "ours": 'שלנו',
        "scored": 'הוערך',
        "method": 'שיטה, טקסט ייחוס והרצה',
        "not_measured": 'עוד לא נמדד על קבוצה מוחזקת בצד',
        "phist_nm": 'עוד לא נמדד על קבוצה מוחזקת בצד. קבוצת המבחן של הדפוס ההיסטורי ממתינה לטקסטי ייחוס ממתנדבים; לא יוצג מספר עד שהיא תוערך.',
        "release_note": 'לא נפרסם מודלים או גרסה של צינור העיבוד עד שנשיג תוצאות טובות יותר מהכלים הקיימים לפחות בסוג מסמך אחד.',
    },
}
ICON = {"info": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6"></circle><path d="M8 7.3v3.5M8 5.1v.1"></path></svg>'}
NA = '<td class="num na">–</td>'
e = html.escape


def page(lang: str, R: dict) -> str:
    """Build a status report from real-world held-out results only."""
    t = T[lang]
    json_href = f"{shell.prefix(lang)}benchmarks/results.json"
    historical = R["p_hist"]
    hand = R["handwriting"]
    historical_scored = historical.get("status") == "scored"
    handwriting_scored = hand.get("status") == "scored"
    toc = [
        ("p-mod", e(t["pmod_h"]), e(t["not_measured"])),
        ("p-hist", e(t["phist_h"]), e(t["scored"] if historical_scored else t["not_measured"])),
        ("handwriting", e(t["hand_h"]), e(t["scored"] if handwriting_scored else t["not_measured"])),
    ]
    historical_section = phist_section(t, historical) if historical_scored else empty(
        "p-hist", t["phist_h"], t["not_measured"], t["phist_nm"],
    )
    handwriting_section = hand_section(t, hand) if handwriting_scored else empty(
        "handwriting", t["hand_h"], t["not_measured"], t["hand_t"],
    )
    return "".join([
        shell.head(lang, e(t["title"]), e(t["desc"]), "bench"),
        shell.header(lang, "bench"),
        '<main id="main" class="bench">\n',
        shell.page_head(e(t["title"]), f'<p class="lede">{t["lede"].format(json=json_href)}</p>\n'
                                       f'<p class="note">{e(t["release_note"])}</p>\n'
                                       f'<p class="note">{e(t["updated"].format(d=R["updated"]))}</p>'),
        shell.toc(lang, toc),
        f'<section id="p-mod" class="wrap domain">{domain_head(e(t["pmod_h"]), e(t["not_measured"]))}</section>\n',
        historical_section,
        handwriting_section,
        "</main>\n",
        shell.footer([f'<p><a href="{json_href}">results.json</a> · <a href="./">HeOCR</a></p>']),
        shell.tail(lang),
    ])


def cell_html(v, ci):
    if v is None:
        return NA
    civ = f'<span class="ci"><bdi dir="ltr">{hc.interval(ci)}%</bdi></span>' if ci else ""
    return f'<td class="num"><span class="v"><bdi dir="ltr">{hc.pct(v)}</bdi></span>{civ}</td>'


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


def pct(v):
    return "–" if v is None else f'<bdi dir="ltr">{v:.1f}%</bdi>'


def pct_ci(v, ci):
    if v is None: return NA
    c = f'<span class="ci"><bdi dir="ltr">{ci[0]:.1f}–{ci[1]:.1f}%</bdi></span>' if ci else ""
    return f'<td class="num"><span class="v"><bdi dir="ltr">{v:.1f}%</bdi></span>{c}</td>'


def hand_section(t, H):
    c1, c2, c3 = t["hw_cols"]; src = H["source"]; me = H["model_effect"]
    rows = []
    for r, lab in t["hw_readers"].items():
        v = H["readers"][r]
        rows.append(f'<tr{" class=\"ours\"" if r.startswith("heocr") and r != "heocr_stockheb" else ""}><th scope="row">{e(lab)}</th>'
                    f'{pct_ci(v["cer"], v["cer_ci95"])}<td class="num"><span class="v">{pct(v["wer"])}</span></td>'
                    f'<td class="num"><span class="v">{pct(v["coverage"])}</span></td></tr>')
    tab = (f'<div class="tablewrap narrow"><table>\n<thead><tr><th scope="col"></th><th scope="col">{e(c1)}</th><th scope="col">{e(c2)}</th>'
           f'<th scope="col">{e(c3)}</th></tr></thead>\n<tbody>\n' + "\n".join(rows) + "\n</tbody></table></div>")
    find = t["hw_finding"].format(d=f'{me["delta_cer"]:+.1f}', lo=f'{me["ci95"][0]:+.1f}', hi=f'{me["ci95"][1]:+.1f}')
    credit = t["hw_credit"].format(name=e(src["name"]), url=e(src["url"]), corpus=e(src["corpus_url"]), licence=e(src["licence"]))
    return (f'<section id="handwriting" class="wrap domain">\n'
            f'{domain_head(e(t["hand_h"]), e(t["scored"]) + " <bdi dir=\"ltr\">" + e(H["scored"]) + "</bdi>", " scored")}\n'
            f'<p class="sub">{e(t["hw_sub"])}</p>\n<p class="warn">{ICON["info"]}<span>{e(find)}</span></p>\n{tab}\n'
            f'<p class="note">{e(t["hw_caveat"])}</p>\n<p class="note">{credit}</p>\n'
            + method(t, [(t["f_measure"], e(H["measure"])), (t["f_interval"], e(H["interval"])), (t["f_run"], e(H["registration"]))]) + "\n</section>\n")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    R = json.loads(RESULTS.read_text(encoding="utf-8"))
    stale = []
    for lang, path in (("he", ROOT / "benchmarks.html"), ("en", ROOT / "en" / "benchmarks.html")):
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
