"""Build htext.html (Hebrew, root) and en/htext.html from htext/corpora.json.

    python3 scripts/build_htext.py                       # write both pages
    python3 scripts/build_htext.py --check               # exit 1 if a committed page is out of date
    python3 scripts/build_htext.py --import-card pby PATH/corpus_card.json
                                                         # refresh one corpus's counts from its htext card, then build

Standard library only. The markup follows the "Bounding Box" design (design/brand-handover/site/htext.html): styles are
site.css and the shell is scripts/shell.py, as on every page.
When htext publishes a corpus or a new version, add or update its entry in corpora.json (counts come from the
corpus card in HeOCR/htext, data/<corpus>/<version>/corpus_card.json), then rebuild.
"""
from __future__ import annotations

import argparse, html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shell  # noqa: E402  (head, header, footer: one source for every page)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "htext" / "corpora.json"

T = {
    "en": {
        "title": "htext",
        "desc": "htext: openly licensed Hebrew text for training Hebrew OCR, in three releases (CC0, CC BY, CC BY-SA), with a rights record for every entry.",
        "lede": "Openly licensed Hebrew text for training HeOCR's recognizers, cut into lines, plain and with niqqud: public-domain text first, and attribution and share-alike text in their own releases. Every work or document carries its own rights record: its status in Israel and in the US, its licence and its credit line. htext is published as three releases, one per licence, so you can pick the terms you need; the core release is CC0 and can be used without conditions.",
        "updated": "Updated {d}. Figures come from each corpus card and are rebuilt from <a href=\"{json}\">corpora.json</a>.",
        "toc": [("what", "What htext is"), ("releases", "Releases"), ("corpora", "Corpora"), ("rights", "Rights"), ("use", "Download and use"),
                ("credit", "Credit"), ("licence", "Licence")],
        "what_p": [
            "htext collects Hebrew text whose rights are clear enough to publish openly, and turns it into training lines for "
            "<a href=\"https://github.com/HeOCR/hocrsyngen\">hocrsyngen</a>, HeOCR's synthetic page generator. The generator "
            "renders each line onto synthetic pages, so the recognizers learn real Hebrew vocabulary, spelling and punctuation, "
            "not only made-up text.",
            "Each source has its own builder, its own corpus and its own card. A build reads a pinned copy of the source, "
            "computes rights per entry, cleans and cuts the text, and checks that no line overlaps HeOCR's evaluation text. "
            "Only the files a card lists are published.",
        ],
        "stat_lines": "lines", "stat_works": "works", "stat_works_laws": "works and laws", "stat_works_laws_books": "works, laws and books", "stat_corpora": "corpora", "stat_corpus": "corpus", "stat_bytes": "of text",
        "corpora_h": "Corpora",
        "releases_h": "Releases",
        "releases_p": "htext ships one release per licence. Pick the release whose terms fit your use. Models trained on any of them can still be released under an open licence, with credit in their NOTICE.",
        "r_contents": "Contains", "r_allows": "You may", "r_licence": "Licence",
        "r_status": {"published": "published", "planned": "planned"},
        "c_in": "Release",
        "planned_h": "Planned sources",
        "planned_p": "Sources being prepared. Each is published only after its rights are checked entry by entry.",
        "c_source": "Source", "c_release": "Release", "c_card": "Corpus card", "c_prev": "Earlier version", "c_issues": "known issues", "c_withdrawn": "withdrawn {d}: its files overlapped HeOCR's evaluation text", "c_withdrawn_corpus": "Withdrawn {d}. A corrected check by HeOCR's evaluation found that these files share text with its evaluation sets, so they were taken down from GitHub, Hugging Face and Zenodo. HeOCR keeps a private backup; decontaminated versions will be published as new versions.", "c_status_withdrawn": "withdrawn", "c_zenodo": "Zenodo (DOI)", "c_zenodo_all": "all versions", "c_hf": "Hugging Face", "c_hf_filtered": "Corrected check: zero shared 6-grams across 16 evaluation pools for these exact text files", "c_hf_same": "the same files as the GitHub release", "c_works": "{w} of {c} catalogue works have lines in this corpus; {u} also in the Israel + US variant.",
        "th_file": "File", "th_variant": "Variant", "th_subset": "Subset", "th_lines": "Lines", "th_works": "Works", "th_laws": "Laws", "th_books": "Books", "th_size": "Size",
        "th_pages": "Articles", "th_sittings": "Sittings",
        "c_privacy": "The private-name filter removed {lines} lines before publication.",
        "c_laws": "{w} of {c} laws in the catalogue have lines in this corpus.",
        "c_books": "All {w} books have lines in this corpus, in both forms. The pointed and plain files hold the same verses, so the totals above count them once.",
        "c_quality": {"transcription": "Text: transcribed by people.",
                      "ocr_layer": "Text: the OCR layer of the scans, filtered against a lexicon. An eye check of {k} random lines against the scans found an error in {l} ({lr}) and {ww} wrong words of {sw} ({wr})."},
        "total": "Total",
        "variant": {"il": "Israel", "il_us": "Israel + US"},
        "subset": {"plain": "plain", "niqqud": "niqqud", "ocr_layer": "OCR layer", "transcription": "transcription"},
        "variants_note": "<b>Israel</b>: every line comes from a work that is public domain in Israel. <b>Israel + US</b>: the subset that is also public domain in the US. <b>niqqud</b> lines are pointed; <b>plain</b> lines carry no points.",
        "rights_h": "Rights",
        "rights_p": [
            "Every entry has a rights record with two fields, <code>pd_israel</code> and <code>pd_us</code>, each with the basis it was computed from and the year it holds for. A corpus variant includes an entry only if its record passes that variant's rule. The records are published with each corpus.",
            "A translation counts as public domain only if both its author and its translator are. Every entry also records its source licence and credit line, so each release can be rebuilt and filtered. No release takes text under a non-commercial (NC) or no-derivatives (ND) licence, and text never crosses releases: a CC0 build never contains a CC BY or CC BY-SA line.",
            "The rights fields are the project's reading of the law, not legal advice.",
        ],
        "rights_basis": "Basis, {n}",
        "use_h": "Download and use",
        "use_p": "Use the release links above to download the text files. The corpus cards and SHA-256 checksums are in the source repository. Every file is UTF-8 with one line per row, NFC normalised, with no blank lines.",
        "use_steps": "Download the files and check them against the published checksums:",
        "use_gen": "Use a file as training text for hocrsyngen, which records it as <code>external:sha256:&lt;hex&gt;</code>:",
        "use_build": "Or rebuild a corpus from its source: each corpus has a build guide in the repository, for example <a href=\"{doc}\">the PBY guide</a>.",
        "credit_h": "Credit",
        "credit_p": "Follow the attribution terms for CC BY and CC BY-SA material. For CC0 material, HeOCR also asks that you carry these acknowledgements into dataset or model cards:",
        "licence_h": "Licence",
        "licence_p": "Each release carries its own licence, listed under <a href=\"#releases\">Releases</a>; the CC BY and CC BY-SA terms bind the source text. HeOCR's own processing and metadata, meaning the rights and line indexes, exclusion lists, cards and checksums, are dedicated to the public domain under <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0 1.0</a> in every release, as far as they can be separated from the text. The builder code is under the <a href=\"https://github.com/HeOCR/htext/blob/main/LICENSE\">MIT licence</a>.",
        "footer": "Created by <a href=\"http://www.shaypalachy.com/\">Shay Palachy Affek</a> and the HeOCR maintainers.",
        "mb": "{x} MB",
    },
    "he": {
        "title": "htext",
        "desc": "htext: טקסט עברי ברישיונות פתוחים לאימון OCR עברי, בשלוש גרסאות (CC0,‏ CC BY,‏ CC BY-SA), עם רישום זכויות לכל פריט.",
        "lede": "טקסט עברי ברישיונות פתוחים לאימון מנועי הזיהוי של HeOCR, חתוך לשורות, עם ניקוד ובלעדיו: בראש ובראשונה טקסט בנחלת הכלל, וטקסט בייחוס ובשיתוף זהה בגרסאות נפרדות. לכל יצירה או מסמך יש רישום זכויות משלו: מעמדו בישראל ובארה\"ב, הרישיון שלו ושורת הקרדיט שלו. htext מתפרסם בשלוש גרסאות, אחת לכל רישיון, כדי שתוכלו לבחור את התנאים שמתאימים לכם; גרסת הליבה היא CC0 ואפשר להשתמש בה בלי תנאים.",
        "updated": "עודכן ב־{d}. המספרים לקוחים מכרטיס כל מאגר ונבנים מחדש מתוך <a href=\"{json}\">corpora.json</a>.",
        "toc": [("what", "מה זה htext"), ("releases", "גרסאות"), ("corpora", "מאגרים"), ("rights", "זכויות"), ("use", "הורדה ושימוש"),
                ("credit", "קרדיט"), ("licence", "רישיון")],
        "what_p": [
            "htext אוסף טקסט עברי שזכויותיו ברורות דיין לפרסום פתוח, והופך אותו לשורות אימון עבור "
            "<a href=\"https://github.com/HeOCR/hocrsyngen\">hocrsyngen</a>, מחולל העמודים הסינתטיים של HeOCR. המחולל "
            "מצייר כל שורה על עמודים סינתטיים, כך שמנועי הזיהוי לומדים אוצר מילים, כתיב ופיסוק עבריים אמיתיים, "
            "ולא רק טקסט מומצא.",
            "לכל מקור יש בונה משלו, מאגר משלו וכרטיס משלו. בנייה קוראת עותק נעוץ של המקור, מחשבת זכויות לכל פריט, "
            "מנקה וחותכת את הטקסט, ובודקת ששום שורה אינה חופפת לטקסט ההערכה של HeOCR. "
            "רק הקבצים שהכרטיס מונה מתפרסמים.",
        ],
        "stat_lines": "שורות", "stat_works": "יצירות", "stat_works_laws": "יצירות וחוקים", "stat_works_laws_books": "יצירות, חוקים וספרים", "stat_corpora": "מאגרים", "stat_corpus": "מאגר", "stat_bytes": "טקסט",
        "corpora_h": "מאגרים",
        "releases_h": "גרסאות",
        "releases_p": "htext מתפרסם בגרסה אחת לכל רישיון. בחרו את הגרסה שתנאיה מתאימים לשימוש שלכם. מודלים שאומנו על כל אחת מהן עדיין יכולים להתפרסם ברישיון פתוח, עם קרדיט בקובץ ה־NOTICE שלהם.",
        "r_contents": "תוכן", "r_allows": "מותר", "r_licence": "רישיון",
        "r_status": {"published": "פורסמה", "planned": "מתוכננת"},
        "c_in": "גרסת htext",
        "planned_h": "מקורות מתוכננים",
        "planned_p": "מקורות בהכנה. כל אחד מתפרסם רק אחרי שזכויותיו נבדקו פריט אחר פריט.",
        "c_source": "מקור", "c_release": "גרסה", "c_card": "כרטיס המאגר", "c_prev": "גרסה קודמת", "c_issues": "בעיות ידועות", "c_withdrawn": "הוסרה ב־{d}: הקבצים שלה חפפו לטקסט ההערכה של HeOCR", "c_withdrawn_corpus": "הוסר ב־{d}. בדיקה מתוקנת של צוות ההערכה של HeOCR מצאה שהקבצים חולקים טקסט עם מערכי ההערכה, ולכן הם הורדו מ־GitHub, מ־Hugging Face ומ־Zenodo. ל־HeOCR יש גיבוי פרטי; גרסאות מנוקות יפורסמו כגרסאות חדשות.", "c_status_withdrawn": "הוסר", "c_zenodo": "Zenodo (DOI)", "c_zenodo_all": "כל הגרסאות", "c_hf": "Hugging Face", "c_hf_filtered": "בבדיקה המתוקנת נמצאו אפס רצפים משותפים של שש מילים מול 16 מאגרי הערכה, עבור קובצי הטקסט האלה", "c_hf_same": "אותם קבצים כמו בגרסה ב־GitHub", "c_works": "ל־{w} מתוך {c} יצירות בקטלוג יש שורות במאגר; ל־{u} מהן גם בגרסת ישראל + ארה\"ב.",
        "th_file": "קובץ", "th_variant": "גרסה", "th_subset": "סוג", "th_lines": "שורות", "th_works": "יצירות", "th_laws": "חוקים", "th_books": "ספרים", "th_size": "גודל",
        "th_pages": "ערכים", "th_sittings": "ישיבות",
        "c_privacy": "מסנן השמות של אנשים פרטיים הסיר {lines} שורות לפני הפרסום.",
        "c_laws": "ל־{w} מתוך {c} חוקים בקטלוג יש שורות במאגר.",
        "c_books": "לכל {w} הספרים יש שורות במאגר, בשתי הצורות. שני הקבצים, המנוקד והלא־מנוקד, מכילים את אותם פסוקים, ולכן הסיכומים למעלה סופרים אותם פעם אחת.",
        "c_quality": {"transcription": "טקסט: הוקלד בידי אנשים.",
                      "ocr_layer": "טקסט: שכבת ה־OCR של הסריקות, מסוננת מול מילון. בבדיקה בעין של {k} שורות אקראיות מול הסריקות נמצאה טעות ב־{l} ({lr}), ו־{ww} מילים שגויות מתוך {sw} ({wr})."},
        "total": "סה\"כ",
        "variant": {"il": "ישראל", "il_us": "ישראל + ארה\"ב"},
        "subset": {"plain": "ללא ניקוד", "niqqud": "מנוקד", "ocr_layer": "שכבת OCR", "transcription": "תעתיק"},
        "variants_note": "<b>ישראל</b>: כל שורה לקוחה מיצירה שבנחלת הכלל בישראל. <b>ישראל + ארה\"ב</b>: תת־הקבוצה שבנחלת הכלל גם בארה\"ב. שורות <b>מנוקדות</b> כוללות ניקוד; שורות <b>ללא ניקוד</b> אינן כוללות.",
        "rights_h": "זכויות",
        "rights_p": [
            "לכל פריט יש רישום זכויות עם שני שדות, <code>pd_israel</code> ו־<code>pd_us</code>, וכל אחד מציין את הבסיס שלפיו חושב ואת השנה שבה הוא תקף. גרסת מאגר כוללת פריט רק אם הרישום שלו עומד בכלל של אותה גרסה. הרישומים מתפרסמים עם כל מאגר.",
            "תרגום נחשב נחלת הכלל רק אם גם המחבר וגם המתרגם בנחלת הכלל. כל פריט מתעד גם את רישיון המקור ואת שורת הקרדיט שלו, כך שאפשר לבנות ולסנן כל גרסה מחדש. אף גרסה אינה כוללת טקסט ברישיון לא־מסחרי (NC) או ללא יצירות נגזרות (ND), וטקסט לעולם אינו עובר בין גרסאות: בנייה של CC0 לעולם אינה כוללת שורה ב־CC BY או ב־CC BY-SA.",
            "שדות הזכויות הם קריאת הפרויקט את החוק, ולא ייעוץ משפטי.",
        ],
        "rights_basis": "בסיס, {n}",
        "use_h": "הורדה ושימוש",
        "use_p": "להורדת קובצי הטקסט השתמשו בקישורי הגרסאות למעלה. כרטיסי המאגרים וסיכומי SHA-256 נמצאים במאגר הקוד. כל קובץ הוא UTF-8, שורה אחת לכל רשומה, מנורמל ל־NFC וללא שורות ריקות.",
        "use_steps": "הורידו את הקבצים ובדקו אותם מול סיכומי הביקורת שפורסמו:",
        "use_gen": "השתמשו בקובץ כטקסט אימון ל־hocrsyngen, שמתעד אותו כ־<code>external:sha256:&lt;hex&gt;</code>:",
        "use_build": "או בנו מאגר מחדש מהמקור: לכל מאגר יש מדריך בנייה במאגר הקוד, למשל <a href=\"{doc}\">המדריך של פרויקט בן־יהודה</a>.",
        "credit_h": "קרדיט",
        "credit_p": "יש לפעול לפי תנאי הייחוס של רישיונות CC BY ו־CC BY-SA. גם בשימוש בחומר ברישיון CC0, ‏HeOCR מבקש לציין את הקרדיט בכרטיס מאגר הנתונים או המודל:",
        "licence_h": "רישיון",
        "licence_p": "לכל גרסה יש רישיון משלה, כמפורט תחת <a href=\"#releases\">גרסאות</a>; תנאי CC BY ו־CC BY-SA חלים על טקסט המקור. העיבוד והמטא־דאטה של HeOCR, כלומר אינדקסי הזכויות והשורות, רשימות ההחרגה, הכרטיסים וסיכומי הביקורת, מוקדשים לנחלת הכלל ברישיון <a href=\"https://creativecommons.org/publicdomain/zero/1.0/deed.he\">CC0 1.0</a> בכל הגרסאות, ככל שאפשר להפריד אותם מהטקסט. קוד הבנייה ברישיון <a href=\"https://github.com/HeOCR/htext/blob/main/LICENSE\">MIT</a>.",
        "footer": "נוצר בידי <a href=\"http://www.shaypalachy.com/\">שי פלצ'י אפק</a> ומתחזקי HeOCR.",
        "mb": "{x} MB",
    },
}

e = html.escape


def n(x: int) -> str:
    return f"{x:,}"


def mb(lang: str, b: int) -> str:
    return '<span dir="ltr">' + T[lang]["mb"].format(x=f"{b / 1e6:,.1f}") + "</span>"


def table(head, rows, total=None):
    s = ['<div class="tablewrap"><table>\n<thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead>\n<tbody>\n"]
    for r in rows:
        s.append("<tr>" + "".join(f'<td{" class=\"num\"" if num else ""}>{v}</td>' for v, num in r) + "</tr>\n")
    if total:
        s.append('<tr class="total">' + "".join(f'<td{" class=\"num\"" if num else ""}>{v}</td>' for v, num in total) + "</tr>\n")
    s.append("</tbody></table></div>\n")
    return "".join(s)


def zenodo_item(c: dict, t: dict) -> str:
    if not (record := c.get("zenodo")):
        return ""
    doi = e(record["doi"])
    link = f'<a href="https://doi.org/{doi}"><span dir="ltr">{doi}</span></a>'
    if concept := record.get("concept_doi"):
        concept = e(concept)
        link += f' ({t["c_zenodo_all"]}: <a href="https://doi.org/{concept}"><span dir="ltr">{concept}</span></a>)'
    return f'<li>{t["c_zenodo"]}: {link}</li>\n'


def page(lang: str, R: dict) -> str:
    t = T[lang]
    pre = shell.prefix(lang)
    json_href = f"{pre}htext/corpora.json"
    C = R["corpora"]
    live = [c for c in C if not c.get("withdrawn")]
    out = []
    w = out.append
    w(shell.head(lang, e(t["title"]), e(t["desc"]), "htext"))
    w(shell.header(lang, "htext"))
    w(shell.page_head(e(t["title"]), f'<p class="lede">{t["lede"]}</p>\n'
                                      f'<p class="note">{t["updated"].format(d=e(R["updated"]), json=json_href)}</p>'))
    w(shell.toc(lang, [(i, e(h), None) for i, h in t["toc"]]))
    w('<main id="main" class="wrap doc ht">\n')
    # Count full-coverage files once. The IL+US variant and alternate forms repeat text.
    full_files = [f for c in live for f in c["files"] if f.get("variant") != "il_us" and not f.get("same_text_as")]
    lines = sum(f["lines"] for f in full_files)
    bytes_ = sum(f["bytes"] for f in full_files)
    works = sum(c.get("works_in_corpus", 0) for c in live)
    all_works_known = all("works_in_corpus" in c for c in live)
    units = {c.get("unit", "works") for c in live}
    works_label = t["stat_works_laws_books"] if "books" in units else t["stat_works_laws"] if "laws" in units else t["stat_works"]
    # --- 1. What
    w(f'<section id="what">\n<h2>{e(dict(t["toc"])["what"])}</h2>\n')
    for p in t["what_p"]:
        w(f"<p>{p}</p>\n")
    w('<div class="stats">'
      f'<div class="stat"><b>{n(lines)}</b><span>{t["stat_lines"]}</span></div>'
      + (f'<div class="stat"><b>{n(works)}</b><span>{works_label}</span></div>' if all_works_known else '')
      + f'<div class="stat"><b>{mb(lang, bytes_)}</b><span>{t["stat_bytes"]}</span></div>'
      f'<div class="stat"><b>{len(live)}</b><span>{t["stat_corpus"] if len(live) == 1 else t["stat_corpora"]}</span></div>'
      "</div>\n</section>\n")
    # --- 1b. Releases
    rel = {r["id"]: r for r in R["releases"]}
    w(f'<section id="releases">\n<h2>{e(t["releases_h"])}</h2>\n<p>{e(t["releases_p"])}</p>\n')
    for r in R["releases"]:
        w(f'<h3>{e(r["name"])}</h3>\n<span class="status">{e(t["r_status"][r["status"]])}</span>'
          f'<span class="status">{e(r["licence"]["name"])}</span>\n<ul class="facts">\n'
          f'<li>{t["r_contents"]}: {e(r["contents"][lang])}</li>\n'
          f'<li>{t["r_allows"]}: {e(r["allows"][lang])}</li>\n'
          f'<li>{t["r_licence"]}: <a href="{e(r["licence"]["url"])}">{e(r["licence"]["name"])}</a></li>\n</ul>\n')
    w("</section>\n")
    # --- 2. Corpora
    w(f'<section id="corpora">\n<h2>{e(t["corpora_h"])}</h2>\n')
    for c in C:
        w(f'<h3 id="{e(c["id"])}">{e(c["name"][lang])}</h3>\n')
        if c.get("withdrawn"):
            w(f'<span class="status">{e(t["c_status_withdrawn"])}</span><span class="status">{e(rel[c["htext_release"]]["name"])}</span>\n')
            w(f'<p>{e(c["description"][lang])}</p>\n<p class="note">{e(t["c_withdrawn_corpus"].format(d=c["withdrawn"]))}</p>\n')
            w('<ul class="facts">\n'
              f'<li>{t["c_source"]}: <a href="{e(c["source"]["url"])}">{e(c["source"]["name"][lang])}</a> ({e(c["source_licence"][lang])})</li>\n'
              f'<li>{t["c_release"]}: <a href="{e(c["release"]["url"])}">{e(c["release"]["tag"])}</a> ({t["c_issues"]}: <a href="{e(c["card_url"].replace("CORPUS_CARD.md", "KNOWN_ISSUES.md"))}">KNOWN_ISSUES.md</a>)</li>\n'
              "</ul>\n")
            continue
        w(f'<span class="status">{e(c["release"]["tag"])}</span><span class="status">{e(rel[c["htext_release"]]["name"])}</span>\n')
        w(f'<p>{e(c["description"][lang])}</p>\n')
        unit = c.get("unit", "works")
        count_key = "works" if unit in {"works", "laws", "books"} else unit
        show_counts = all(count_key in f for f in c["files"])
        show_variant = any("variant" in f for f in c["files"])
        headers = [t["th_file"]]
        if show_variant:
            headers.append(t["th_variant"])
        headers.extend([t["th_subset"], t["th_lines"]])
        if show_counts:
            headers.append(t[f"th_{unit}"])
        rows = []
        for f in c["files"]:
            row = [(f'<code>{e(f["name"])}</code>', False)]
            if show_variant:
                row.append((e(t["variant"].get(f.get("variant"), "—")), False))
            row.extend([(e(t["subset"][f["subset"]]), False), (n(f["lines"]), True)])
            if show_counts:
                row.append((n(f[count_key]), True))
            rows.append(row + [(mb(lang, f["bytes"]), True)])
        w(table([*headers, t["th_size"]], rows))
        if any(f.get("variant") == "il_us" for f in c["files"]):
            w(f'<p class="note">{t["variants_note"]}</p>\n')
        q = c.get("text_quality")
        if q == "ocr_layer":
            k = c["eye_check"]
            quality = t["c_quality"][q].format(k=n(k["lines_checked"]), l=n(k["lines_with_error"]), lr=f'{k["lines_with_error"] / k["lines_checked"]:.0%}',
                                               ww=n(k["words_wrong"]), sw=n(k["sample_words"]), wr=f'{k["words_wrong"] / k["sample_words"]:.1%}')
        else:
            quality = t["c_quality"][q] if q else ""
        count = ""
        if "works_in_corpus" in c:
            count = (t[f"c_{unit}"].format(w=n(c["works_in_corpus"]), c=n(c["catalogue_works"])) if unit != "works"
                 else t["c_works"].format(w=n(c["works_in_corpus"]), c=n(c["catalogue_works"]), u=n(c["works_in_il_us"])))
        release = rel[c["htext_release"]]
        licence = release["licence"]
        hf = c.get("hf", {})
        w('<ul class="facts">\n'
          f'<li>{t["c_in"]}: {e(release["name"])} (<a href="{e(licence["url"])}">{e(licence["name"])}</a>)</li>\n'
          f'<li>{t["c_source"]}: <a href="{e(c["source"]["url"])}">{e(c["source"]["name"][lang])}</a> ({e(c["source_licence"][lang])})</li>\n'
          f'<li>{t["c_release"]}: <a href="{e(c["release"]["url"])}">{e(c["release"]["tag"])}</a>, {e(c["release"]["date"])}</li>\n'
          f'<li>{t["c_card"]}: <a href="{e(c["card_url"])}">CORPUS_CARD.md</a></li>\n'
          + "".join(f'<li>{t["c_prev"]}: '
                    + (f'{e(p["tag"])}, {e(t["c_withdrawn"].format(d=p["withdrawn"]))}' if p.get("withdrawn") else f'<a href="{e(p["url"])}">{e(p["tag"])}</a>')
                    + (f' (<a href="{e(p["known_issues_url"])}">{t["c_issues"]}</a>)' if p.get("known_issues_url") else "")
                    + "</li>\n" for p in c.get("previous", []))
          + zenodo_item(c, t)
          + (f'<li>{t["c_hf"]}: <a href="{e(c["release"]["url"] if hf.get("revision") else "https://huggingface.co/datasets/" + hf["repo"])}">{e(hf["repo"])}</a> '
             f'({e(t["c_hf_filtered"] if hf["filtered"] else t["c_hf_same"])})</li>\n' if "filtered" in hf else "")
          + (f'<li>{e(quality)}</li>\n' if quality else '')
          + (f'<li>{e(count)}</li>\n' if count else '')
          + (f'<li>{e(t["c_privacy"].format(lines=n(c["privacy_lines_dropped"])))}</li>\n'
             if "privacy_lines_dropped" in c else '')
          + "</ul>\n")
    if R.get("planned"):
        w(f'<h3 id="planned">{e(t["planned_h"])}</h3>\n<p>{e(t["planned_p"])}</p>\n<ul class="facts">\n')
        for p in R["planned"]:
            w(f'<li><b>{e(p["name"][lang])}</b>: {e(p["note"][lang])}</li>\n')
        w("</ul>\n")
    w("</section>\n")
    # --- 3. Rights
    w(f'<section id="rights">\n<h2>{e(t["rights_h"])}</h2>\n')
    for p in t["rights_p"]:
        w(f"<p>{p}</p>\n")
    w('<ul class="facts">\n')
    for c in C:
        w(f'<li><b>{e(c["source"]["name"][lang])}</b>: {e(c["rights_basis"][lang])}</li>\n')
    w("</ul>\n</section>\n")
    # --- 4. Use
    first = next((c for c in live if c["release"]["url"].startswith("https://github.com/")), live[0])
    sums = first["sha256sums_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    w(f'<section id="use">\n<h2>{e(t["use_h"])}</h2>\n<p>{t["use_p"]}</p>\n<p>{t["use_steps"]}</p>\n')
    w("<pre><code>" + e(f"gh release download {first['release']['tag']} -R HeOCR/htext\n"
                         f"curl -LO {sums}\n"
                         f"grep -E '_{first['version']}\\.txt$' SHA256SUMS | sha256sum -c") + "</code></pre>\n")
    w(f'<p>{t["use_gen"]}</p>\n')
    w("<pre><code>" + e(f"hocrsyngen ... --text-corpus {first['files'][0]['name']}") + "</code></pre>\n")
    w(f'<p>{t["use_build"].format(doc="https://github.com/HeOCR/htext/blob/main/docs/pby_corpus.md")}</p>\n</section>\n')
    # --- 5. Credit
    w(f'<section id="credit">\n<h2>{e(t["credit_h"])}</h2>\n<p>{e(t["credit_p"])}</p>\n')
    for c in C:
        if c.get("credit"):
            w(f'<p class="credit">Credit: <a href="{e(c["credit"]["url"])}">{e(c["credit"]["text"]["en"])}</a>'
              + (f' · קרדיט: <a href="{e(c["credit"]["url"])}">{e(c["credit"]["text"]["he"])}</a>' if lang == "he" else "")
              + "</p>\n")
    w("</section>\n")
    # --- 6. Licence
    w(f'<section id="licence">\n<h2>{e(t["licence_h"])}</h2>\n<p>{t["licence_p"]}</p>\n</section>\n')
    w("</main>\n")
    w(shell.footer([f"<p>{t['footer']}</p>",
                    f'<p><a href="{R["repository"]}">HeOCR/htext</a> · <a href="{json_href}">corpora.json</a> · <a href="./">HeOCR</a></p>']))
    w(shell.tail(lang))
    return "".join(out)


def import_card(R: dict, cid: str, path: Path) -> None:
    """Refresh one corpus entry's file counts from an htext corpus_card.json."""
    card = json.loads(path.read_text(encoding="utf-8"))
    entry = next((c for c in R["corpora"] if c["id"] == cid), None)
    if entry is None:
        sys.exit(f"no corpus '{cid}' in corpora.json: add its entry (names, source, rights, credit, release) first")
    previous = {f["name"]: f for f in entry["files"]}
    files = []
    for name, info in card["files"].items():
        row = {**previous.get(name, {}), "name": name}
        row.update({k: info[k] for k in ("lines", "bytes", "sha256")})
        row.update({k: info[k] for k in ("variant", "subset", "works", "pages", "sittings") if k in info})
        if "text_quality" in info:
            row.setdefault("subset", info["text_quality"])
        files.append(row)
    entry["files"] = files
    rights = card.get("rights", {})
    if "catalogue_rows" in card["source"]:
        entry["catalogue_works"] = card["source"]["catalogue_rows"]
    for key in ("works_in_corpus", "works_in_il_us"):
        if key in rights:
            entry[key] = rights[key]
    privacy = card.get("privacy", {})
    if "lines_dropped" in privacy:
        entry["privacy_lines_dropped"] = privacy["lines_dropped"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--import-card", nargs=2, metavar=("CORPUS_ID", "CARD_JSON"))
    a = ap.parse_args()
    R = json.loads(DATA.read_text(encoding="utf-8"))
    if a.import_card:
        import_card(R, a.import_card[0], Path(a.import_card[1]))
        DATA.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stale = []
    for lang, path in (("he", ROOT / "htext.html"), ("en", ROOT / "en" / "htext.html")):
        s = page(lang, R)
        if a.check:
            if not path.exists() or path.read_text(encoding="utf-8") != s:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(s, encoding="utf-8")
    if stale:
        print("out of date:", ", ".join(stale), "— run python3 scripts/build_htext.py", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
