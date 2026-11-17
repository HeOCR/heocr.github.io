"""Build htext.html and he/htext.html from htext/corpora.json.

    python3 scripts/build_htext.py                       # write both pages
    python3 scripts/build_htext.py --check               # exit 1 if a committed page is out of date
    python3 scripts/build_htext.py --import-card pby PATH/corpus_card.json
                                                         # refresh one corpus's counts from its htext card, then build

Standard library only. The page styles are taken from rights.html and he/rights.html, as on the Benchmarks page.
When htext publishes a corpus or a new version, add or update its entry in corpora.json (counts come from the
corpus card in HeOCR/htext, data/<corpus>/<version>/corpus_card.json), then rebuild.
"""
from __future__ import annotations

import argparse, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "htext" / "corpora.json"

EXTRA_CSS = """
  .ht section { max-width: none; }
  .ht h2 { margin-top: 0; }
  .ht h3 { font-size: 1.05rem; margin: 26px 0 4px; }
  .status { display: inline-block; background: var(--tag); color: var(--muted); padding: 2px 10px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin: 0 6px 10px 0; margin-inline-end: 6px; }
  .tablewrap { overflow-x: auto; margin: 8px 0 6px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
  table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
  th, td { padding: 8px 12px; text-align: start; border-bottom: 1px solid var(--line); vertical-align: top; white-space: nowrap; }
  tr:last-child td { border-bottom: 0; }
  tr.total td { font-weight: 600; }
  th { font-weight: 600; color: var(--muted); font-size: 0.82rem; }
  td.num { font-variant-numeric: tabular-nums; }
  td code, li code, p code { font-size: 0.85em; }
  .facts { font-size: 0.9rem; margin: 6px 0 0; }
  .facts li { margin: 0 0 4px; }
  .credit { border-inline-start: 3px solid var(--accent); padding: 2px 0; padding-inline-start: 12px; margin: 10px 0; }
  .toc { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 8px; }
  .toc a { font-size: 0.9rem; }
  pre { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; overflow-x: auto; font-size: 0.85rem; direction: ltr; text-align: left; }
  .stats { display: flex; flex-wrap: wrap; gap: 12px; margin: 10px 0 4px; }
  .stat { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 10px 16px; min-width: 140px; }
  .stat b { display: block; font-size: 1.35rem; font-variant-numeric: tabular-nums; }
  .stat span { color: var(--muted); font-size: 0.85rem; }
"""

T = {
    "en": {
        "title": "htext",
        "desc": "htext: public-domain Hebrew text for training Hebrew OCR, with a rights record for every entry. CC0.",
        "lede": "Public-domain Hebrew text for training HeOCR's recognizers, cut into lines, plain and with niqqud. Every work or document carries its own rights record: public domain in Israel, and its US status. All of it is released under CC0, so it can be used without conditions.",
        "back": "← HeOCR", "other": "עברית", "other_href": "he/htext.html", "home": "./",
        "updated": "Updated {d}. Figures come from each corpus card and are rebuilt from <a href=\"{json}\">corpora.json</a>.",
        "toc": [("what", "What htext is"), ("corpora", "Corpora"), ("rights", "Rights"), ("use", "Download and use"),
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
        "stat_lines": "lines", "stat_works": "works", "stat_corpora": "corpora", "stat_corpus": "corpus", "stat_bytes": "of text",
        "corpora_h": "Corpora",
        "planned_h": "Planned sources",
        "planned_p": "Sources being prepared. Each is published only after its rights are checked entry by entry.",
        "c_source": "Source", "c_release": "Release", "c_card": "Corpus card", "c_works": "{w} of {c} catalogue works have lines in this corpus; {u} also in the Israel + US variant.",
        "th_file": "File", "th_variant": "Variant", "th_subset": "Subset", "th_lines": "Lines", "th_works": "Works", "th_size": "Size",
        "total": "Total",
        "variant": {"il": "Israel", "il_us": "Israel + US"},
        "subset": {"plain": "plain", "niqqud": "niqqud"},
        "variants_note": "<b>Israel</b>: every line comes from a work that is public domain in Israel. <b>Israel + US</b>: the subset that is also public domain in the US. <b>niqqud</b> lines are pointed; <b>plain</b> lines carry no points.",
        "rights_h": "Rights",
        "rights_p": [
            "Every entry has a rights record with two fields, <code>pd_israel</code> and <code>pd_us</code>, each with the basis it was computed from and the year it holds for. A corpus variant includes an entry only if its record passes that variant's rule. The records are published with each corpus.",
            "A translation counts as public domain only if both its author and its translator are. htext takes no text under a licence with conditions (no NC, ND or share-alike text), so nothing in it limits how the data can be used.",
            "The rights fields are the project's reading of the law, not legal advice.",
        ],
        "rights_basis": "Basis, {n}",
        "use_h": "Download and use",
        "use_p": "The corpus files are assets of each corpus's GitHub release, and the card, checksums and rights index are in the repository. Every file is UTF-8 with one line per row, NFC normalised, with no blank lines.",
        "use_steps": "Download the files and check them against the published checksums:",
        "use_gen": "Use a file as training text for hocrsyngen, which records it as <code>external:sha256:&lt;hex&gt;</code>:",
        "use_build": "Or rebuild a corpus from its source: each corpus has a build guide in the repository, for example <a href=\"{doc}\">the PBY guide</a>.",
        "credit_h": "Credit",
        "credit_p": "Credit is not required by the licence, but some sources ask for it, and HeOCR gives it. Please carry these lines into any dataset or model card that uses a corpus:",
        "licence_h": "Licence",
        "licence_p": "The data, meaning the text files, rights and line indexes, exclusion lists, cards and checksums, is dedicated to the public domain under <a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0 1.0</a>. The builder code is under the <a href=\"https://github.com/HeOCR/htext/blob/main/LICENSE\">MIT licence</a>.",
        "footer": "Created by <a href=\"http://www.shaypalachy.com/\">Shay Palachy Affek</a> and the HeOCR maintainers.",
        "mb": "{x} MB",
    },
    "he": {
        "title": "htext",
        "desc": "htext: טקסט עברי בנחלת הכלל לאימון OCR עברי, עם רישום זכויות לכל פריט. CC0.",
        "lede": "טקסט עברי בנחלת הכלל לאימון מנועי הזיהוי של HeOCR, חתוך לשורות, עם ניקוד ובלעדיו. לכל יצירה או מסמך יש רישום זכויות משלו: נחלת הכלל בישראל, והמעמד בארה\"ב. הכול משוחרר ברישיון CC0, ואפשר להשתמש בו בלי תנאים.",
        "back": "← HeOCR", "other": "English", "other_href": "../htext.html", "home": "./",
        "updated": "עודכן ב־{d}. המספרים לקוחים מכרטיס כל מאגר ונבנים מחדש מתוך <a href=\"{json}\">corpora.json</a>.",
        "toc": [("what", "מה זה htext"), ("corpora", "מאגרים"), ("rights", "זכויות"), ("use", "הורדה ושימוש"),
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
        "stat_lines": "שורות", "stat_works": "יצירות", "stat_corpora": "מאגרים", "stat_corpus": "מאגר", "stat_bytes": "טקסט",
        "corpora_h": "מאגרים",
        "planned_h": "מקורות מתוכננים",
        "planned_p": "מקורות בהכנה. כל אחד מתפרסם רק אחרי שזכויותיו נבדקו פריט אחר פריט.",
        "c_source": "מקור", "c_release": "גרסה", "c_card": "כרטיס המאגר", "c_works": "ל־{w} מתוך {c} יצירות בקטלוג יש שורות במאגר; ל־{u} מהן גם בגרסת ישראל + ארה\"ב.",
        "th_file": "קובץ", "th_variant": "גרסה", "th_subset": "סוג", "th_lines": "שורות", "th_works": "יצירות", "th_size": "גודל",
        "total": "סה\"כ",
        "variant": {"il": "ישראל", "il_us": "ישראל + ארה\"ב"},
        "subset": {"plain": "ללא ניקוד", "niqqud": "מנוקד"},
        "variants_note": "<b>ישראל</b>: כל שורה לקוחה מיצירה שבנחלת הכלל בישראל. <b>ישראל + ארה\"ב</b>: תת־הקבוצה שבנחלת הכלל גם בארה\"ב. שורות <b>מנוקדות</b> כוללות ניקוד; שורות <b>ללא ניקוד</b> אינן כוללות.",
        "rights_h": "זכויות",
        "rights_p": [
            "לכל פריט יש רישום זכויות עם שני שדות, <code>pd_israel</code> ו־<code>pd_us</code>, וכל אחד מציין את הבסיס שלפיו חושב ואת השנה שבה הוא תקף. גרסת מאגר כוללת פריט רק אם הרישום שלו עומד בכלל של אותה גרסה. הרישומים מתפרסמים עם כל מאגר.",
            "תרגום נחשב נחלת הכלל רק אם גם המחבר וגם המתרגם בנחלת הכלל. htext אינו כולל טקסט ברישיון עם תנאים (לא NC, לא ND ולא שיתוף זהה), ולכן דבר בו אינו מגביל את השימוש בנתונים.",
            "שדות הזכויות הם קריאת הפרויקט את החוק, ולא ייעוץ משפטי.",
        ],
        "rights_basis": "בסיס, {n}",
        "use_h": "הורדה ושימוש",
        "use_p": "קובצי המאגר מצורפים לגרסת ה־GitHub של כל מאגר, והכרטיס, סיכומי הביקורת ואינדקס הזכויות נמצאים במאגר הקוד. כל קובץ הוא UTF-8, שורה אחת לכל רשומה, מנורמל ל־NFC וללא שורות ריקות.",
        "use_steps": "הורידו את הקבצים ובדקו אותם מול סיכומי הביקורת שפורסמו:",
        "use_gen": "השתמשו בקובץ כטקסט אימון ל־hocrsyngen, שמתעד אותו כ־<code>external:sha256:&lt;hex&gt;</code>:",
        "use_build": "או בנו מאגר מחדש מהמקור: לכל מאגר יש מדריך בנייה במאגר הקוד, למשל <a href=\"{doc}\">המדריך של פרויקט בן־יהודה</a>.",
        "credit_h": "קרדיט",
        "credit_p": "הרישיון אינו מחייב קרדיט, אבל חלק מהמקורות מבקשים אותו, ו־HeOCR נותן אותו. אנא העבירו את השורות האלה לכל כרטיס מאגר נתונים או מודל שמשתמש במאגר:",
        "licence_h": "רישיון",
        "licence_p": "הנתונים, כלומר קובצי הטקסט, אינדקסי הזכויות והשורות, רשימות ההחרגה, הכרטיסים וסיכומי הביקורת, מוקדשים לנחלת הכלל ברישיון <a href=\"https://creativecommons.org/publicdomain/zero/1.0/deed.he\">CC0 1.0</a>. קוד הבנייה ברישיון <a href=\"https://github.com/HeOCR/htext/blob/main/LICENSE\">MIT</a>.",
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


def page(lang: str, R: dict) -> str:
    t = T[lang]
    style_src = (ROOT / ("he/rights.html" if lang == "he" else "rights.html")).read_text(encoding="utf-8")
    style = re.search(r"<style>(.*?)</style>", style_src, re.S).group(1)
    pre = "../" if lang == "he" else ""
    json_href = f"{pre}htext/corpora.json"
    C = R["corpora"]
    out = []
    w = out.append
    # --- head (same structure as the Benchmarks page)
    w(f'<!doctype html>\n<html lang="{lang}"{" dir=\"rtl\"" if lang == "he" else ""}>\n<head>\n<meta charset="utf-8">\n'
      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      f'<title>{e(t["title"])}</title>\n<meta name="description" content="{e(t["desc"])}">\n')
    fonts = ("family=Frank+Ruhl+Libre:wght@500;700&family=Heebo:wght@400;500;600&family=Inter:wght@400;500;600"
             if lang == "he" else "family=Frank+Ruhl+Libre:wght@500;700&family=Inter:wght@400;500;600")
    w('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
      f'<link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">\n')
    w(f"<style>{style}{EXTRA_CSS}</style>\n")
    w('<link rel="alternate" hreflang="en" href="https://heocr.github.io/htext.html">\n'
      '<link rel="alternate" hreflang="he" href="https://heocr.github.io/he/htext.html">\n</head>\n<body>\n\n')
    # --- header
    cur = '<span aria-current="page" lang="{0}">{1}</span>'.format(lang, "עברית" if lang == "he" else "English")
    oth = f'<a href="{t["other_href"]}" lang="{"en" if lang == "he" else "he"}" hreflang="{"en" if lang == "he" else "he"}">{t["other"]}</a>'
    w(f'<header>\n  <div class="wrap">\n    <nav class="langbar" aria-label="{"שפה / Language" if lang == "he" else "Language / שפה"}">\n'
      f'      <div class="lang-toggle">\n        {cur}\n        {oth}\n      </div>\n    </nav>\n'
      f'    <a class="back" href="{t["home"]}">{t["back"]}</a>\n    <h1>{e(t["title"])}</h1>\n'
      f'    <p class="lede">{t["lede"]}</p>\n'
      f'    <p class="note">{t["updated"].format(d=e(R["updated"]), json=json_href)}</p>\n  </div>\n</header>\n\n')
    w('<main class="wrap doc ht">\n')
    w('<nav class="toc">' + " · ".join(f'<a href="#{i}">{e(h)}</a>' for i, h in t["toc"]) + "</nav>\n")
    # --- totals: the "il" variant holds every published line; il_us is its subset
    lines = sum(f["lines"] for c in C for f in c["files"] if f["variant"] == "il")
    bytes_ = sum(f["bytes"] for c in C for f in c["files"] if f["variant"] == "il")
    works = sum(c["works_in_corpus"] for c in C)
    # --- 1. What
    w(f'<section id="what">\n<h2>{e(dict(t["toc"])["what"])}</h2>\n')
    for p in t["what_p"]:
        w(f"<p>{p}</p>\n")
    w('<div class="stats">'
      f'<div class="stat"><b>{n(lines)}</b><span>{t["stat_lines"]}</span></div>'
      f'<div class="stat"><b>{n(works)}</b><span>{t["stat_works"]}</span></div>'
      f'<div class="stat"><b>{mb(lang, bytes_)}</b><span>{t["stat_bytes"]}</span></div>'
      f'<div class="stat"><b>{len(C)}</b><span>{t["stat_corpus"] if len(C) == 1 else t["stat_corpora"]}</span></div>'
      "</div>\n</section>\n")
    # --- 2. Corpora
    w(f'<section id="corpora">\n<h2>{e(t["corpora_h"])}</h2>\n')
    for c in C:
        w(f'<h3 id="{e(c["id"])}">{e(c["name"][lang])}</h3>\n')
        w(f'<span class="status">{e(c["release"]["tag"])}</span><span class="status">CC0</span>\n')
        w(f'<p>{e(c["description"][lang])}</p>\n')
        rows = [((f'<code>{e(f["name"])}</code>', False), (e(t["variant"][f["variant"]]), False),
                 (e(t["subset"][f["subset"]]), False), (n(f["lines"]), True), (n(f["works"]), True),
                 (mb(lang, f["bytes"]), True)) for f in c["files"]]
        w(table([t["th_file"], t["th_variant"], t["th_subset"], t["th_lines"], t["th_works"], t["th_size"]], rows))
        w(f'<p class="note">{t["variants_note"]}</p>\n')
        w('<ul class="facts">\n'
          f'<li>{t["c_source"]}: <a href="{e(c["source"]["url"])}">{e(c["source"]["name"][lang])}</a> ({e(c["source_licence"][lang])})</li>\n'
          f'<li>{t["c_release"]}: <a href="{e(c["release"]["url"])}">{e(c["release"]["tag"])}</a>, {e(c["release"]["date"])}</li>\n'
          f'<li>{t["c_card"]}: <a href="{e(c["card_url"])}">CORPUS_CARD.md</a></li>\n'
          f'<li>{e(t["c_works"].format(w=n(c["works_in_corpus"]), c=n(c["catalogue_works"]), u=n(c["works_in_il_us"])))}</li>\n'
          "</ul>\n")
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
    first = C[0]
    sums = first["sha256sums_url"].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    w(f'<section id="use">\n<h2>{e(t["use_h"])}</h2>\n<p>{t["use_p"]}</p>\n<p>{t["use_steps"]}</p>\n')
    w("<pre><code>" + e(f"gh release download {first['release']['tag']} -R HeOCR/htext\n"
                         f"curl -LO {sums}\n"
                         f"grep -E '_v1\\.txt$' SHA256SUMS | sha256sum -c") + "</code></pre>\n")
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
    w("</main>\n\n<footer>\n  <div class=\"wrap\">\n"
      f'    <p>{t["footer"]}</p>\n    <p><a href="{R["repository"]}">HeOCR/htext</a> · <a href="{json_href}">corpora.json</a> · <a href="{t["home"]}">HeOCR</a></p>\n'
      "  </div>\n</footer>\n\n</body>\n</html>\n")
    return "".join(out)


def import_card(R: dict, cid: str, path: Path) -> None:
    """Refresh one corpus entry's file counts from an htext corpus_card.json."""
    card = json.loads(path.read_text(encoding="utf-8"))
    entry = next((c for c in R["corpora"] if c["id"] == cid), None)
    if entry is None:
        sys.exit(f"no corpus '{cid}' in corpora.json: add its entry (names, source, rights, credit, release) first")
    entry["files"] = [{"name": k, "variant": v["variant"], "subset": v["subset"], "lines": v["lines"],
                       "works": v["works"], "bytes": v["bytes"], "sha256": v["sha256"]} for k, v in card["files"].items()]
    rights = card.get("rights", {})
    entry["catalogue_works"] = card["source"].get("catalogue_rows", entry.get("catalogue_works"))
    entry["works_in_corpus"] = rights.get("works_in_corpus", entry.get("works_in_corpus"))
    entry["works_in_il_us"] = rights.get("works_in_il_us", entry.get("works_in_il_us"))


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
    for lang, path in (("en", ROOT / "htext.html"), ("he", ROOT / "he" / "htext.html")):
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
