"""Internal build: static handoff previews + Design-canvas artboards, both from
results.json, the fixed wording of the current pages, site.css and hero_chart.py."""
import json, re, sys, os, datetime
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1])                       # .../current
OUT_H = HERE / "handoff"
OUT_T = HERE / "twins"
OUT_C = HERE.parent / "canvas" / "project"
sys.path.insert(0, str(OUT_H))
import hero_chart as hc                       # noqa: E402

R = json.loads((SRC / "benchmarks/results.json").read_text(encoding="utf-8"))
CSS = (OUT_H / "site.css").read_text(encoding="utf-8")
OLD = {
    ("bench", "en"): (SRC / "benchmarks.html").read_text(encoding="utf-8"),
    ("bench", "he"): (SRC / "he/benchmarks.html").read_text(encoding="utf-8"),
    ("home", "en"): (SRC / "index.html").read_text(encoding="utf-8"),
    ("home", "he"): (SRC / "he/index.html").read_text(encoding="utf-8"),
}
HEIGHTS = json.loads((HERE / "heights.json").read_text()) if (HERE / "heights.json").exists() else {}

FONTS = ("https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700"
         "&family=Heebo:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap")

T = {
    "en": dict(
        dir="ltr", nav_bench="Benchmarks", nav_htext="htext", nav_rights="Rights &amp; takedown",
        nav_aria="Site", lang_aria="Language / שפה", theme="Night mode", skip="Skip to content",
        toc_aria="On this page", kicker="Documents by format", chart_title="Character error by document type",
        lower="lower is better", ours="ours",
        lg_alt="Best other open tool", lg_alt_s="the lowest of Docling, MarkItDown and PyMuPDF4LLM",
        lg_tess="Stock Tesseract", lg_tess_s="heb, tessdata_best",
        run="Run", gate_label="Release gate", gate_not_run="not run", gate_run="run",
        axis_note="One linear axis from 0 to 100%; bars start at zero. Whiskers show the interval ({interval}). "
                  "Where an interval is narrower than its marker, read it from the numbers beside it.",
        more="Documents by format: every reader and every measure",
        scored="Scored", interval_key="Interval:",
        gate_sub="The release gate scores a fresh set, made after the code is frozen. "
                 "Each document type then gets one verdict: supported, or not supported.",
        gate_count="<strong>{d}</strong> of {n} document types have a verdict",
        v_supported="Supported", v_unsupported="Not supported", v_pending="Awaiting run",
        method="Method, reference and run", foot_aria="Footer",
        cell_note="A dash means the reader has no score on that measure. An empty cell means the measure does not apply to that document type. The last column holds a measure that exists for one type only; its name is in that type's heading row.",
    ),
    "he": dict(
        dir="rtl", nav_bench="מדדי ביצועים", nav_htext="htext", nav_rights="זכויות והסרה",
        nav_aria="ניווט באתר", lang_aria="שפה / Language", theme="מצב לילה", skip="דילוג לתוכן",
        toc_aria="בעמוד זה", kicker="מסמכים לפי פורמט", chart_title="שגיאת תווים לפי סוג מסמך",
        lower="נמוך יותר עדיף", ours="שלנו",
        lg_alt="הכלי הפתוח האחר הטוב ביותר", lg_alt_s="הנמוך ביותר מבין Docling,‏ MarkItDown ו־PyMuPDF4LLM",
        lg_tess="Tesseract הרגיל", lg_tess_s="heb, tessdata_best",
        run="הרצה", gate_label="שער השחרור", gate_not_run="עוד לא הורץ", gate_run="הורץ",
        axis_note="ציר ליניארי אחד, מ־0 עד 100%; הפסים מתחילים באפס. הקווים עם הקצוות מסמנים את רווח הסמך ({interval}). "
                  "כשהרווח צר מהסמן, הוא מופיע במספרים שלצידו.",
        more="מסמכים לפי פורמט: כל הקוראים וכל המדדים",
        scored="הוערך", interval_key="רווח סמך:",
        gate_sub="שער השחרור מעריך קבוצה חדשה, שנוצרת אחרי שהקוד מוקפא. "
                 "לכל סוג מסמך ניתנת אז החלטה אחת: נתמך או לא נתמך.",
        gate_count="ל־<strong>{d}</strong> מתוך {n} סוגי מסמכים יש החלטה",
        v_supported="נתמך", v_unsupported="לא נתמך", v_pending="ממתין להרצה",
        method="שיטה, טקסט ייחוס והרצה", foot_aria="כותרת תחתונה",
        cell_note="קו מפריד פירושו שלקורא אין ציון במדד הזה. תא ריק פירושו שהמדד אינו חל על סוג המסמך הזה. בעמודה האחרונה מופיע מדד שקיים רק לסוג מסמך אחד; שמו מופיע בשורת הכותרת של אותו סוג.",
    ),
}

ICON = {
    "moon": '<svg class="ico i-moon" viewBox="0 0 16 16" aria-hidden="true"><path d="M13 9.6A5.6 5.6 0 0 1 6.4 3 5.6 5.6 0 1 0 13 9.6z"></path></svg>',
    "sun": '<svg class="ico i-sun" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3"></circle><path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"></path></svg>',
    "info": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6"></circle><path d="M8 7.3v3.5M8 5.1v.1"></path></svg>',
    "supported": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.6l3 3 6-7.2"></path></svg>',
    "unsupported": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"></path></svg>',
    "pending": '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.6"></circle><path d="M8 4.9V8l2 1.3"></path></svg>',
}

# ---------- scraping the fixed wording from today's pages ----------
def section(html, sid):
    return re.search(rf'<section id="{sid}">(.*?)</section>', html, re.S).group(1)

def one(pat, s):
    m = re.search(pat, s, re.S)
    return m.group(1) if m else None

def every(pat, s):
    return re.findall(pat, s, re.S)

# ---------- shared components ----------
def header(lang, page, toggle, home_href="./"):
    t = T[lang]
    old = OLD[(page, lang)]
    lt = one(r'<div class="lang-toggle">(.*?)</div>', old).strip()
    cur = ' aria-current="page"'
    nav = (f'<a href="benchmarks.html"{cur if page == "bench" else ""}>{t["nav_bench"]}</a>'
           f'<a href="htext.html">{t["nav_htext"]}</a><a href="rights.html">{t["nav_rights"]}</a>')
    return f'''<a class="skip" href="#main">{t["skip"]}</a>
<header class="site-header">
<div class="wrap bar">
<a class="brand" href="{home_href}">HeOCR</a>
<nav class="site-nav" aria-label="{t["nav_aria"]}">{nav}</nav>
<div class="tools">
<div class="lang-toggle" role="group" aria-label="{t["lang_aria"]}">
{lt}
</div>
<button class="theme-toggle" type="button" {toggle}>{ICON["moon"]}{ICON["sun"]}<span class="label">{t["theme"]}</span></button>
</div>
</div>
</header>'''

def footer(lang, page):
    old = OLD[(page, lang)]
    ps = every(r'(<p>.*?</p>)', one(r'<footer>(.*?)</footer>', old))
    return f'''<footer class="site-footer">
<div class="wrap foot">
<div class="foot-brand">HeOCR</div>
<div class="foot-text">
{chr(10).join(ps)}
</div>
</div>
</footer>'''

def verdict(kind, lang, lg=False, label=None):
    t = T[lang]
    return f'<span class="verdict {kind}{" lg" if lg else ""}">{ICON[kind]}{label or t["v_" + kind]}</span>'

def num(x):
    return f'<bdi dir="ltr">{hc.pct(x)}</bdi>'

def cell_html(value, ci):
    civ = f'<span class="ci"><bdi dir="ltr">{hc.interval(ci)}%</bdi></span>' if ci else ''
    return f'<td class="num"><span class="v">{num(value)}</span>{civ}</td>'

NA = '<td class="num na">–</td>'

# ---------- hero chart ----------
def hero(lang, doc=None, bare=False):
    t = T[lang]
    doc = doc or R["documents"]
    old_doc = section(OLD[("bench", lang)], "documents")
    sub = one(r'<p class="sub">(.*?)</p>', old_doc)
    caveat = sub[sub.index("heocr מפותח" if lang == "he" else "heocr is developed"):]
    interval = one(rf'<li><strong>{t["interval_key"]}</strong> (.*?)</li>', old_doc)
    gate = t["gate_not_run"] if doc["gate"] == "not_run" else t["gate_run"]
    gate_cls = "pending" if doc["gate"] == "not_run" else "supported"
    svgs = hc.hero_svg(doc, lang, "wide") + "\n" + hc.hero_svg(doc, lang, "narrow")
    if bare:
        return svgs
    return f'''<figure class="wrap hero-chart" id="hero">
<div class="panel">
<p class="kicker">{t["kicker"]}</p>
<div class="hc-title"><h2>{t["chart_title"]}</h2><span class="dir">{t["lower"]}</span></div>
<p class="hc-finding">{hc.finding_sentence(doc, lang)}</p>
{legend(lang)}
{svgs}
<figcaption class="hc-foot">
<p class="hc-run"><span>{t["run"]} <code>{escape(doc["run"])}</code></span><span><bdi dir="ltr">{R["updated"]}</bdi></span>{verdict(gate_cls, lang, label=t["gate_label"] + ": " + gate)}</p>
<p class="note">{caveat}</p>
<p class="note">{t["axis_note"].format(interval=interval)}</p>
<p class="note"><a href="#documents">{t["more"]}</a></p>
</figcaption>
</div>
</figure>'''

def legend(lang):
    t = T[lang]
    return f'''<ul class="hc-legend">
<li class="ours">{hc.legend_marker("ours")}<span><b>heocr</b> <small>{t["ours"]}</small></span></li>
<li>{hc.legend_marker("alt")}<span><b>{t["lg_alt"]}</b> <small>{t["lg_alt_s"]}</small></span></li>
<li>{hc.legend_marker("tess")}<span><b>{t["lg_tess"]}</b> <small>{t["lg_tess_s"]}</small></span></li>
</ul>'''

# ---------- tables ----------
STD = ("cer", "wer", "number_recall", "labels", "silent_loss", "image_word_recall")
TBL = ("rows_read", "rows_silent", "cer", "number_recall")
EXTRA = ("labels", "image_word_recall")      # one format-specific measure, shown in the last column
UP = {"number_recall", "labels", "image_word_recall", "rows_read"}
READERS = (("heocr", "heocr"), ("stock", "Tesseract (tessdata_best heb)"), ("docling", "Docling"),
           ("markitdown", "MarkItDown"), ("pymupdf4llm", "PyMuPDF4LLM"))

def slug(code):
    return "doc-" + code.lower().replace(" ", "-")

def th(label_html, metric):
    name = re.sub(r'\s*<span class="ci">.*?</span>', '', label_html).strip()
    direction = one(r'<span class="ci">(.*?)</span>', label_html)
    return name, f'<span class="dir{" up" if metric in UP else ""}">{direction}</span>'

def present(cell):
    return set().union(*[set(r) - {"documents"} for r in cell["readers"].values()])

def metric_labels(lang):
    """Column wording, taken from today's page so it stays as it is."""
    old = section(OLD[("bench", lang)], "documents")
    theads = [every(r'<th>(.*?)</th>', x) for x in every(r'<thead><tr>(.*?)</tr></thead>', old)]
    labels, reader = {}, None
    for cell, ths in zip(R["documents"]["cells"].values(), theads):
        cols = [m for m in (TBL if "rows_read" in present(cell) else STD) if m in present(cell)]
        assert len(cols) == len(ths) - 1
        reader = ths[0]
        for m, o in zip(cols, ths[1:]):
            labels.setdefault(m, o)
    return reader, labels

def docs_tables(lang, codes=None, verdicts=None, with_notes=True):
    """One grouped table for the text formats, one for scanned tables."""
    t = T[lang]
    old = section(OLD[("bench", lang)], "documents")
    h3s = dict(zip(R["documents"]["cells"], every(r'<h3>(.*?) <span class="note">(.*?)</span></h3>', old)))
    notes = every(r'<p class="note">(.*?)</p>', old)
    reader_label, labels = metric_labels(lang)
    cells = {c: v for c, v in R["documents"]["cells"].items() if codes is None or c in codes}
    verdicts = verdicts or {}
    out = []
    for order, pick in ((STD, lambda c: "rows_read" not in present(c)), (TBL, lambda c: "rows_read" in present(c))):
        group = {c: v for c, v in cells.items() if pick(v)}
        if not group:
            continue
        cols = [m for m in order if m not in EXTRA and any(m in present(v) for v in group.values())]
        has_extra = any(m in present(v) for v in group.values() for m in EXTRA)
        head = [f'<th scope="col">{reader_label}</th>']
        for m in cols:
            name, direction = th(labels[m], m)
            head.append(f'<th scope="col">{name}{direction}</th>')
        if has_extra:
            head.append('<td class="thx"></td>')
        out.append(f'<div class="tablewrap"><table>\n<thead><tr>{"".join(head)}</tr></thead>')
        for code, cell in group.items():
            title, meta = h3s[code]
            badge = verdict(verdicts[code], lang) if code in verdicts else ''
            gnote = f'<span class="gnote">{notes[0]}</span>' if (code == "PDF T4" and with_notes) else ''
            mine = present(cell)
            extra = next((m for m in EXTRA if m in mine), None)
            colh = ''
            if extra:
                name, direction = th(labels[extra], extra)
                ns = {r[extra]["n"] for r in cell["readers"].values() if extra in r}
                ntag = f'<span class="tag-n">n = {min(ns)}</span>' if len(ns) == 1 and ns != {cell["documents"]} else ''
                colh = f'<th class="colh" scope="col">{name}{direction.replace("</span>", ntag + "</span>")}</th>'
            span = len(cols) + 1 + (1 if has_extra and not extra else 0)
            out.append(f'<tbody>\n<tr class="group"><th colspan="{span}" scope="rowgroup" id="{slug(code)}">'
                       f'<span class="gtitle">{title} <span class="note">{meta}</span>{badge}{gnote}</span></th>{colh}</tr>')
            for key, name in READERS:
                if key not in cell["readers"]:
                    continue
                r = cell["readers"][key]
                ours = key == "heocr"
                label = name + (f'<span class="tag-ours">{t["ours"]}</span>' if ours else '')
                if r["documents"] != cell["documents"]:
                    label += f'<span class="tag-n block">n = {r["documents"]}</span>'
                tds = []
                for m in cols + ([extra] if extra else [None] if has_extra else []):
                    if m is None or m not in mine:
                        tds.append('<td class="nap"></td>')
                    elif m not in r:
                        tds.append(NA)
                    else:
                        tds.append(cell_html(r[m]["value"], r[m]["ci95"]))
                cls = ' class="ours"' if ours else ''
                out.append(f'<tr{cls}><td>{label}</td>{"".join(tds)}</tr>')
            out.append('</tbody>')
        out.append('</table></div>')
    return "\n".join(out)

def hist_table(lang):
    p = R["p_hist"]
    old = section(OLD[("bench", lang)], "p-hist")
    h3s = every(r'<h3>(.*?) <span class="note">(.*?)</span></h3>', old)
    ths = every(r'<th>(.*?)</th>', one(r'<thead><tr>(.*?)</tr></thead>', old))
    notes = every(r'<p class="note">(.*?)</p>', old)
    head = [f'<th scope="col">{ths[0]}</th>']
    for m, o in zip(("cer", "wer"), ths[1:]):
        name, direction = th(o, m)
        head.append(f'<th scope="col">{name}{direction}</th>')
    out = [f'<div class="tablewrap narrow"><table>\n<thead><tr>{"".join(head)}</tr></thead>']
    for sl, (title, meta) in zip(p["slices"], h3s):
        gnote = f'<span class="gnote">{notes[0]}</span>' if sl["too_small"] else ''
        out.append(f'<tbody>\n<tr class="group"><th colspan="3" scope="rowgroup"><span class="gtitle">{title} <span class="note">{meta}</span>{gnote}</span></th></tr>')
        for key, e in p["engines"].items():
            v = sl["engines"][key]
            name = f'<a href="{e["url"]}">{e["name"]}</a>' if e.get("url") else e["name"]
            if e["ours"]:
                name += f'<span class="tag-ours">{T[lang]["ours"]}</span>'
            tds = cell_html(v["cer"], v["cer_ci95"]) + cell_html(v["wer"], v["wer_ci95"])
            out.append(f'<tr{" class=\"ours\"" if e["ours"] else ""}><td>{name}</td>{tds}</tr>')
        out.append('</tbody>')
    out.append('</table></div>')
    return "\n".join(out), notes[-1]

def method(lang, old_section):
    facts = one(r'(<ul class="facts">.*?</ul>)', old_section)
    return f'<details class="method"><summary>{T[lang]["method"]}</summary>\n{facts}\n</details>'

def domain_head(h2, status, cls=""):
    return f'<div class="domain-head"><h2>{h2}</h2><span class="status{cls}">{status}</span></div>'

def gate_block(lang, verdicts=None):
    """verdicts: {code: 'supported'|'unsupported'}; None or missing = awaiting the run."""
    t = T[lang]
    cells = R["documents"]["cells"]
    verdicts = verdicts or {}
    kinds = [verdicts.get(c, "pending") for c in cells]
    strip = "".join(f'<span class="gate-cell {k}">{"" if k == "pending" else ICON[k]}</span>' for k in kinds)
    decided = sum(k != "pending" for k in kinds)
    if decided == len(kinds):
        count = (f'<strong>{kinds.count("supported")}</strong>{t["v_supported"]}<span class="sep">·</span>'
                 f'<strong>{kinds.count("unsupported")}</strong>{t["v_unsupported"]}')
    else:
        count = t["gate_count"].format(d=decided, n=len(kinds))
    items = "".join(
        f'<li><a href="#{slug(c)}"><span class="code">{c}</span> <span class="name">{hc.TYPE_LABELS[lang][c]}</span></a>{verdict(k, lang)}</li>\n'
        for c, k in zip(cells, kinds))
    return f'''<div class="gate-summary">
<div class="gate-strip" aria-hidden="true">{strip}</div>
<p class="gate-count">{count}</p>
</div>
<ul class="gate-list">
{items}</ul>'''

# ---------- Benchmarks page ----------
def bench_main(lang, part=0):
    t = T[lang]
    old = OLD[("bench", lang)]
    head = one(r'<header>(.*?)</header>', old)
    h1 = one(r'<h1>(.*?)</h1>', head)
    lede = one(r'(<p class="lede">.*?</p>)', head)
    upd = one(r'(<p class="note">.*?</p>)', head)
    toc = every(r'<a href="#([\w-]+)">(.*?)</a>', one(r'<nav class="toc">(.*?)</nav>', old))
    sec = {sid: section(old, sid) for sid, _ in toc}
    status = {}
    for sid, _ in toc:
        st = one(r'<span class="status">(.*?)</span>', sec[sid])
        status[sid] = (st, "") if st else (t["scored"], " scored")
    gate_state = t["gate_not_run"] if R["documents"]["gate"] == "not_run" else t["gate_run"]
    toc_html = "".join(f'<a href="#{sid}">{name}<small>{status[sid][0]}</small></a>' for sid, name in toc)
    toc_html += f'<a href="#gate">{t["gate_label"]}<small>{gate_state[0].upper() + gate_state[1:]}</small></a>'

    def empty(sid):
        s = sec[sid]
        return (f'<section id="{sid}" class="wrap domain">\n{domain_head(one(r"<h2>(.*?)</h2>", s), status[sid][0])}\n'
                f'<div class="empty">{one(r"<div class=.empty.>(.*?)</div>", s)}</div>\n</section>')

    # historical print
    s = sec["p-hist"]
    table, last_note = hist_table(lang)
    hist = f'''<section id="p-hist" class="wrap domain">
{domain_head(one(r"<h2>(.*?)</h2>", s), t["scored"] + ' <bdi dir="ltr">' + R["p_hist"]["scored"] + '</bdi>', " scored")}
<p class="warn">{ICON["info"]}<span>{one(r'<p class="warn">(.*?)</p>', s)}</span></p>
{table}
{method(lang, s)}
<p class="note">{last_note}</p>
</section>'''

    # documents by format
    s = sec["documents"]
    notes = every(r'<p class="note">(.*?)</p>', s)
    docs = f'''<section id="documents" class="wrap domain">
{domain_head(one(r"<h2>(.*?)</h2>", s), t["scored"] + ' <bdi dir="ltr">' + R["updated"] + '</bdi>', " scored")}
<p class="sub">{one(r'<p class="sub">(.*?)</p>', s)}</p>
{docs_tables(lang)}
<p class="legend-note">{t["cell_note"]}</p>
<p class="note">{notes[1]}</p>
<p class="note">{notes[2]}</p>
{method(lang, s)}
</section>'''

    not_run = R["documents"]["gate"] == "not_run"
    sub = one(r'<p class="sub">(.*?)</p>', s)
    fixed = sub[sub.index("שער השחרור עוד לא הורץ" if lang == "he" else "Release gate not yet run"):]
    gate = f'''<section id="gate" class="wrap domain">
<div class="domain-head"><h2>{t["gate_label"]}</h2>{verdict("pending", lang, label=gate_state[0].upper() + gate_state[1:]) if not_run else ""}</div>
<p class="sub">{t["gate_sub"]}{" " + fixed if not_run else ""}</p>
{gate_block(lang)}
</section>'''

    top = f'''<div class="wrap page-head">
<h1>{h1}</h1>
{lede}
{upd}
</div>
{hero(lang)}
<nav class="wrap" aria-label="{t["toc_aria"]}"><div class="toc">{toc_html}</div></nav>
{empty("p-mod")}
{hist}
{empty("handwriting")}'''
    bottom = f'''{docs}
{empty("vendors")}
{gate}'''
    inner = {0: top + "\n" + bottom, 1: top, 2: bottom}[part]
    return f'<main id="main" class="bench">\n{inner}\n</main>'

# ---------- Home page (light refresh: same content, new shell) ----------
def home_main(lang):
    old = OLD[("home", lang)]
    head = one(r'<header>(.*?)</header>', old)
    tagline = one(r'(<p class="(?:he|tag)".*?</p>)', head)
    h1 = one(r'(<h1>.*?</h1>)', head)
    lede = one(r'(<p class="lede">.*?</p>)', head)
    links = one(r'(<div class="links">.*?</div>)', head)
    links = links.replace('class="btn" href="benchmarks.html"', 'class="btn primary" href="benchmarks.html"')
    flow = one(r'(<div class="flow".*?</div>)', head)
    main = one(r'<main class="wrap">(.*?)</main>', old)
    return f'''<div class="home-hero">
<div class="wrap">
{tagline}
{h1}
{lede}
{links}
{flow}
</div>
</div>
<main id="main" class="wrap home">{main}</main>'''

# ---------- page shells ----------
def static_page(lang, title, body, css_href, inline_css=None, extra_head=""):
    t = T[lang]
    css = f'<style>\n{inline_css}\n</style>' if inline_css else f'<link rel="stylesheet" href="{css_href}">'
    theme_js = "" if inline_css else f'<script src="{css_href.replace("site.css", "theme.js")}"></script>\n'
    return f'''<!doctype html>
<html lang="{lang}" dir="{t["dir"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">
{css}
<script>(function(){{try{{if(localStorage.getItem("heocr-theme")==="dark")document.documentElement.dataset.theme="dark"}}catch(e){{}}}})()</script>
{extra_head}</head>
<body class="site">
{body}
{theme_js}</body>
</html>
'''

DC_LOGIC = '''class Component extends DCLogic {
renderVals() {
const base = this.props.theme ?? '%s';
const theme = (this.state && this.state.theme) || base;
return {
theme: theme,
pressed: theme === 'dark' ? 'true' : 'false',
toggleTheme: () => this.setState({ theme: theme === 'dark' ? 'light' : 'dark' })
};
}
}'''

def dc_page(lang, title, body, theme, w, h, links=None, root_extra="", extra_css=""):
    t = T[lang]
    links = links or {}

    def relink(m):
        href = m.group(1)
        if href.startswith(("http", "#", "mailto")):
            return m.group(0)
        return f'href="{links.get(href, "#")}"'

    body = re.sub(r'href="([^"]*)"', relink, body)
    assert "{{" not in body.replace("{{toggleTheme}}", "").replace("{{pressed}}", ""), title
    props = json.dumps({"theme": {"editor": "enum", "options": ["light", "dark"], "default": theme},
                        "$preview": {"width": w, "height": h}})
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">
<style>
body{{margin:0}}
{re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)}{extra_css}
</style>
</helmet>
<div class="site" lang="{lang}" dir="{t["dir"]}" data-theme="{{{{theme}}}}"{root_extra}>
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
{DC_LOGIC % theme}
</script>
</body>
</html>
'''

STATIC_TOGGLE = 'data-theme-toggle aria-pressed="false"'
DC_TOGGLE = 'onClick="{{toggleTheme}}" aria-pressed="{{pressed}}"'

def page_body(page, lang, toggle, part=0):
    main = bench_main(lang, part) if page == "bench" else home_main(lang)
    return ((header(lang, page, toggle) + "\n" if part != 2 else "") + main
            + ("\n" + footer(lang, page) if part != 1 else ""))

TITLES = {("bench", "en"): "HeOCR benchmarks", ("bench", "he"): "מדדי ביצועים של HeOCR",
          ("home", "en"): "HeOCR", ("home", "he"): "HeOCR"}

# ---------- documentation boards ----------
BOARD_CSS = '''
.sheet{padding:56px 60px 64px;display:flex;flex-direction:column;gap:40px}
.sheet-title{font-size:2.5rem;margin:0 0 6px}
.sheet-lede{color:var(--muted);max-width:62em;margin:0}
.spec{display:flex;flex-direction:column;gap:14px}
.spec>h2{font:700 1.2rem/1.3 var(--font-body);border-top:1px solid var(--line-strong);padding-top:16px}
.spec-label{font-size:.78rem;font-weight:600;color:var(--muted);margin:0}
.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;align-items:start}
.trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;align-items:start}
.demo{background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:22px;display:flex;flex-direction:column;gap:14px}
.demo.flush{padding:0;overflow:hidden}
.demo-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.site .demo main h3,.demo h3{margin:0}
.demo .site-footer{margin-top:0}
.demo .empty{max-width:none}
.kv td,.kv th{white-space:normal;vertical-align:top}
.kv td:first-child{font-weight:600;white-space:nowrap}
.kv td.num{white-space:nowrap}
.swatches{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.swatch{border:1px solid var(--line);border-radius:8px;overflow:hidden;font-size:.78rem;line-height:1.4}
.swatch i{display:block;height:52px;border-bottom:1px solid var(--line)}
.swatch div{padding:7px 9px}
.swatch b{display:block;font-family:var(--font-mono);font-weight:600}
.swatch span{color:var(--muted)}
.type-row{display:grid;grid-template-columns:150px minmax(0,1fr) minmax(0,1fr);gap:18px;align-items:baseline;border-bottom:1px solid var(--line);padding:10px 0}
.type-row .spec-label{line-height:1.5}
.hc-demo .hc-narrow{display:block;max-width:360px}
.hc-demo-wide .hc-narrow{display:none}
'''

def tokens():
    def block(sel):
        body = re.search(re.escape(sel) + r'\s*\{(.*?)\n\}', CSS, re.S).group(1)
        return dict(re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6})', body))
    light = block(":root")
    dark = dict(light, **block('[data-theme="dark"]'))
    return light, dark

def lum(hexv):
    c = [int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

PAIRS = [("text", "bg", 4.5), ("text", "surface", 4.5), ("text", "accent-soft", 4.5), ("muted", "bg", 4.5),
         ("muted", "surface", 4.5), ("muted", "tag", 4.5), ("muted", "accent-soft", 4.5), ("accent", "bg", 4.5),
         ("accent", "surface", 4.5), ("accent", "accent-soft", 4.5), ("on-accent", "accent", 4.5),
         ("ok", "ok-soft", 4.5), ("no", "no-soft", 4.5), ("series-ours", "bg", 3), ("series-alt", "bg", 3),
         ("series-tess", "bg", 3), ("line-strong", "bg", 1.3)]

def check_contrast():
    bad = []
    for name, tk in zip(("light", "dark"), tokens()):
        for fg, bg, need in PAIRS:
            c = contrast(tk[fg], tk[bg])
            if c < need:
                bad.append(f"{name}: {fg} on {bg} = {c:.2f} < {need}")
    return bad

def sample_doc(codes):
    d = dict(R["documents"])
    d["cells"] = {c: R["documents"]["cells"][c] for c in codes}
    return d

def board_chart_spec():
    g = hc.GEOM
    sample = sample_doc(["PDF T1", "DOC", "PDF T6", "Scanned tables"])
    wide = hc.hero_svg(sample, "en", "wide")
    def geom_rows():
        rows = [("viewBox width", "W"), ("Axis header height", "TOP"), ("Group height", "GH"), ("Series row pitch", "ROW"),
                ("Plot origin (0%)", "P0"), ("Plot length (0 to 100%)", "PW"), ("Reader name column, start", "NAME"),
                ("Value column, right edge", "VAL"), ("Interval column, right edge", "CI"), ("Bar thickness, heocr", "BAR_OURS"),
                ("Bar thickness, others", "BAR"), ("Circle radius (heocr)", "R"), ("Square side (alternative)", "SQ"),
                ("Diamond half-diagonal (Tesseract)", "DIA"), ("Interval cap half-height", "CAP")]
        return "".join(f'<tr><td>{n}</td><td class="num">{g["wide"][k]}</td><td class="num">{g["narrow"][k]}</td></tr>' for n, k in rows)
    light, dark = tokens()
    def series_row(key, role, mark, weight):
        tok = "series-" + key
        return (f'<tr><td>{hc.legend_marker(key).replace("<svg ", "<svg width=\"14\" height=\"14\" ")} {role}</td><td>{mark}</td>'
                f'<td><code>--{tok}</code></td><td><code>{light[tok]}</code></td><td><code>{dark[tok]}</code></td><td>{weight}</td></tr>')
    body = f'''<div class="sheet">
<div><h1 class="sheet-title">Hero chart specification</h1>
<p class="sheet-lede">Grouped horizontal bars with a marker and a 95% interval whisker, one group per document type, one linear axis from 0 to 100% character error. Generated as static inline SVG by <code>hero_chart.py</code> from <code>documents.cells</code>; all styling is in <code>site.css</code>, so one SVG serves both themes.</p></div>

<div class="spec"><h2>Anatomy and states</h2>
<p class="spec-label">Wide variant (container wider than 820 px), real data for four document types: all three series · no alternative · no Tesseract character-error score · widest interval</p>
<div class="demo hc-demo-wide">{legend("en")}{wide}</div>
<div class="demo hc-demo-wide" data-theme="dark">{legend("en")}{wide}</div>
<p class="spec-label">Narrow variant (container up to 820 px, drawn 1:1 at 343 px on a 375 px phone) · English (LTR) and Hebrew (RTL, mirrored: zero on the right, numbers stay left-to-right)</p>
<div class="trio">
<div class="demo hc-demo">{hc.hero_svg(sample, "en", "narrow")}</div>
<div class="demo hc-demo" dir="rtl" lang="he">{hc.hero_svg(sample, "he", "narrow")}</div>
<div class="demo hc-demo" dir="rtl" lang="he" data-theme="dark">{hc.hero_svg(sample, "he", "narrow")}</div>
</div></div>

<div class="spec"><h2>Series</h2>
<div class="tablewrap"><table class="kv">
<thead><tr><th>Role</th><th>Mark</th><th>Token</th><th>Light</th><th>Night</th><th>Label</th></tr></thead>
<tbody>
{series_row("ours", "heocr", "Filled circle, thicker bar, always the first row", "Bold name and value")}
{series_row("alt", "Best other open tool", "Hollow square; lowest character error among Docling, MarkItDown, PyMuPDF4LLM for that type; the label names the tool", "Regular")}
{series_row("tess", "Stock Tesseract", "Filled diamond; always the third row", "Regular; n shown when it differs from the type")}
</tbody></table></div>
<p class="note">Identity never rests on colour: shape, row position, weight and a direct name label all repeat it. heocr is green and the best other tool is red, a pair that some readers cannot tell apart by hue, which is why the other cues are always present. Text always uses text tokens, never a series colour.</p></div>

<div class="pair">
<div class="spec"><h2>Interval, labels and caption</h2>
<div class="tablewrap"><table class="kv"><tbody>
<tr><td>Bar</td><td>From 0 to the value, series colour at 30% opacity, square ends. Length is the measure; no minimum length.</td></tr>
<tr><td>Interval</td><td>Line from <code>ci95[0]</code> to <code>ci95[1]</code>, 1.5 px, series colour, with end caps. Drawn to scale and never widened; the same interval is always printed in the last column.</td></tr>
<tr><td>Marker</td><td>Centred on the value, 1.5 px ring in <code>--bg</code>.</td></tr>
<tr><td>Numbers</td><td>Same rule as the tables: two decimals under 1%, otherwise one. Tabular figures, right-aligned in both directions.</td></tr>
<tr><td>Axis</td><td>Linear, 0 to 100%, ticks at 0, 25, 50, 75, 100 (0, 50, 100 when narrow). A value above 100% is clamped at the axis end and keeps its true number.</td></tr>
<tr><td>Missing</td><td>A text line in the lane, never a mark: “no other open tool reads this format”, “not scored on this type”, “no character-error score; see table”.</td></tr>
<tr><td>Headline</td><td>Computed, not written: counts the types where heocr is lowest against every reader in the file, whether intervals overlap, and names any type where it is not lowest.</td></tr>
<tr><td>Caption</td><td>Run id · date · gate status badge, then the fixed “not held out” sentence, the axis and interval note, and a link to the tables.</td></tr>
</tbody></table></div></div>

<div class="spec"><h2>Geometry (SVG user units = CSS px at 1:1)</h2>
<div class="tablewrap"><table class="kv">
<thead><tr><th>Dimension</th><th>Wide</th><th>Narrow</th></tr></thead>
<tbody>{geom_rows()}</tbody></table></div>
<p class="note">Height = axis header + number of types × group height + 6. Text: 13 px (12.5 px narrow); axis ticks, column heads and intervals 11.5 px (10.5 px narrow); type descriptors 12 px. Gridlines and separators 1 px in <code>--line</code>; the zero line in <code>--line-strong</code>. Hovering a group tints it with <code>--surface</code>; there is no script.</p>
<h2>Honesty rules built into the generator</h2>
<div class="tablewrap"><table class="kv"><tbody>
<tr><td>Every type</td><td>All entries of <code>documents.cells</code> are drawn in file order, including any where heocr loses or ties.</td></tr>
<tr><td>Axis</td><td>One linear axis from zero. No truncation, no break, no log scale.</td></tr>
<tr><td>Readers</td><td>Only readers present in <code>results.json</code>. Tesseract appears wherever it has a character-error score.</td></tr>
<tr><td>Provenance</td><td>Run, date and gate status sit directly under the plot, with the sentence that these sets are not held out.</td></tr>
</tbody></table></div></div>
</div>
</div>'''
    return body

def board_components():
    en_head = header("en", "bench", DC_TOGGLE)
    he_head = header("he", "bench", 'aria-pressed="false"')
    en_head2 = header("en", "bench", 'aria-pressed="true"')
    old = section(OLD[("bench", "en")], "documents")
    table = docs_tables("en", ["PDF T1", "PDF T6"], {"PDF T1": "supported", "PDF T6": "unsupported"}, with_notes=False)
    title = ''
    empty = '<div class="empty">' + one(r'<div class="empty">(.*?)</div>', section(OLD[("bench", "en")], "p-mod")) + '</div>'
    badges = lambda lang: (f'<div class="demo-row">{verdict("supported", lang)}{verdict("unsupported", lang)}{verdict("pending", lang)}</div>'
                           f'<div class="demo-row">{verdict("supported", lang, lg=True)}{verdict("unsupported", lang, lg=True)}{verdict("pending", lang, lg=True)}</div>')
    example = {c: ("unsupported" if c in ("PDF T4", "PDF T5", "Scanned tables") else "supported") for c in R["documents"]["cells"]}
    interval = f'''<div class="tablewrap"><table class="kv">
<thead><tr><th>State</th><th>Display</th><th>Markup</th></tr></thead><tbody>
<tr><td>Value with interval</td>{cell_html(0.0976, [0.0896, 0.1054])}<td><code>.v</code> + <code>.ci</code>, one line</td></tr>
<tr class="ours"><td>Ours</td>{cell_html(0.0013, [0.0011, 0.0014])}<td><code>tr.ours</code> plus the “ours” tag on the name</td></tr>
<tr><td>No interval (set too small)</td>{cell_html(0.5672, None)}<td><code>.v</code> only; the reason is in the group note</td></tr>
<tr><td>Not measured</td>{NA}<td><code>td.na</code>, an en dash</td></tr>
</tbody></table></div>'''
    statuses = ('<div class="demo-row"><span class="status scored">Scored <bdi dir="ltr">2026-11-11</bdi></span><span class="status">No data yet</span><span class="status">Pending</span>'
                '<span class="dir">lower is better</span><span class="dir up">higher is better</span><span class="tag-ours" style="margin:0">ours</span><span class="tag-n" style="margin:0">n = 80</span></div>'
                '<div class="demo-row"><a class="btn primary" href="#">Benchmarks</a><a class="btn" href="#">GitHub</a><span class="meta"><span>Apache-2.0</span><span>Tesseract 5</span></span></div>')
    meth = method("en", old).replace('<details class="method">', '<details class="method" open>')
    both = lambda inner, cls="": f'<div class="pair"><div class="demo{cls}">{inner}</div><div class="demo{cls}" data-theme="dark">{inner}</div></div>'
    return f'''<div class="sheet">
<div><h1 class="sheet-title">Shared components</h1>
<p class="sheet-lede">Every page uses these pieces from one stylesheet. Each is shown in the default light theme and in night mode. Layout uses logical properties, so the Hebrew pages need no extra rules.</p></div>

<div class="spec"><h2>Header: brand, navigation, language switch, theme toggle</h2>
<p class="spec-label">English, light · the current page is underlined; the language switch is two plain links; the toggle is the only way into night mode</p>
<div class="demo flush">{en_head}</div>
<p class="spec-label">Hebrew, light (mirrored by <code>dir="rtl"</code> alone)</p>
<div class="demo flush" dir="rtl" lang="he">{he_head}</div>
<p class="spec-label">Night mode</p>
<div class="demo flush" data-theme="dark">{en_head2}</div></div>

<div class="spec"><h2>Table, with the “ours” row and interval display</h2>
<p class="spec-label">Real figures for two types. The verdict badges in the group rows are placeholders, to show where they go after the gate run.</p>
{both(title + table)}
{both(interval)}</div>

<div class="spec"><h2>Status chips, direction labels, tags and buttons</h2>
{both(statuses)}</div>

<div class="spec"><h2>No-data card</h2>
{both('<div class="domain-head" style="border:0;padding:0;margin:0"><h2>Modern printed Hebrew</h2><span class="status">No data yet</span></div>' + empty)}</div>

<div class="spec"><h2>Verdict badge</h2>
<p class="spec-label">Three states, two sizes, English and Hebrew. Icon, label and border style all differ, so the verdict never depends on colour.</p>
{both(badges("en") + '<div dir="rtl" lang="he" style="display:flex;flex-direction:column;gap:14px">' + badges("he") + '</div>')}</div>

<div class="spec"><h2>Release-gate summary</h2>
<p class="spec-label">Today: gate not run, straight from <code>results.json</code></p>
{both(gate_block("en"))}
<p class="spec-label">Example only, to show the filled state after a run. These verdicts are placeholders, not results.</p>
{both(gate_block("en", example))}</div>

<div class="spec"><h2>Method disclosure and footer</h2>
{both(meth)}
{both(footer("en", "bench"), " flush")}</div>
</div>'''

def board_tokens():
    light, dark = tokens()
    names = ["bg", "surface", "tag", "accent-soft", "line", "line-strong", "text", "muted", "accent", "on-accent",
             "series-ours", "series-alt", "series-tess", "ok", "ok-soft", "no", "no-soft"]
    exact = {"bg", "surface", "text", "muted", "line", "accent", "accent-soft", "tag"}
    def sw(tk, theme):
        out = []
        for n in names:
            note = "today's value" if (theme == "dark" and n in exact) else ("new" if n not in exact else "refined")
            if theme == "light" and n in ("text", "accent", "accent-soft", "tag"):
                note = "today's value"
            out.append(f'<div class="swatch"><i style="background:var(--{n})"></i><div><b>--{n}</b>{tk[n]}<br><span>{note}</span></div></div>')
        return '<div class="swatches">' + "".join(out) + '</div>'
    def ratios(tk):
        return "".join(f'<tr><td><code>--{fg}</code> on <code>--{bg}</code></td><td class="num">{contrast(tk[fg], tk[bg]):.1f}:1</td><td class="num">{need}:1</td></tr>'
                       for fg, bg, need in PAIRS)
    rt = lambda tk: f'<div class="tablewrap"><table class="kv"><thead><tr><th>Pair</th><th>Contrast</th><th>Needed</th></tr></thead><tbody>{ratios(tk)}</tbody></table></div>'
    def trow(label, style, en, he):
        return (f'<div class="type-row"><p class="spec-label">{label}</p><div style="{style}">{en}</div>'
                f'<div style="{style}" dir="rtl" lang="he">{he}</div></div>')
    types = (
        trow("h1 · Frank Ruhl Libre 700<br>clamp(2.1rem, 3.25rem)", "font:700 3.25rem/1.08 var(--font-display)", "HeOCR benchmarks", "מדדי ביצועים של HeOCR")
        + trow("h2 · Frank Ruhl Libre 700<br>1.6rem", "font:700 1.6rem/1.2 var(--font-display)", "Documents by format", "מסמכים לפי פורמט")
        + trow("h3 · Inter / Heebo 600<br>1.02rem", "font:600 1.02rem/1.35 var(--font-body)", "PDF with a correct text layer", "PDF עם שכבת טקסט תקינה")
        + trow("Lede · 1.12rem / 1.6", "font:400 1.12rem/1.6 var(--font-body)", "How HeOCR compares with other open tools, per kind of document.", "איך HeOCR משתווה לכלים פתוחים אחרים, לפי סוג המסמך.")
        + trow("Body · 1rem / 1.6", "font:400 1rem/1.6 var(--font-body)", "Each table is one kind of document.", "כל טבלה היא סוג מסמך אחד.")
        + trow("Small · 0.9rem<br>tables, notes", "font:400 .9rem/1.6 var(--font-body);color:var(--muted)", "T4 and T5 use the same scanned pages.", "T4 ו־T5 משתמשים באותם עמודים סרוקים.")
        + trow("Micro · 0.78rem<br>intervals, labels", "font:500 .78rem/1.5 var(--font-body);color:var(--muted)", "lower is better · 0.19–0.35%", "נמוך יותר עדיף · <bdi dir=\"ltr\">0.19–0.35%</bdi>")
        + trow("Figures · tabular-nums 500", "font:500 1rem/1.6 var(--font-body);font-variant-numeric:tabular-nums", "0.27%  22.1%  100.0%", "<bdi dir=\"ltr\">0.27%  22.1%  100.0%</bdi>")
        + trow("Code · system mono 0.88em", "font:400 .9rem/1.6 var(--font-mono)", "synth-2026-11-17-main", "<bdi dir=\"ltr\">line_fold_v1</bdi>"))
    return f'''<div class="sheet">
<div><h1 class="sheet-title">Colour and type tokens</h1>
<p class="sheet-lede">CSS custom properties on <code>:root</code> (light, the default whatever the OS setting) and on <code>[data-theme="dark"]</code> (night mode, set only by the toggle). The eight night tokens that exist today are unchanged; the rest are additions the new components need.</p></div>
<div class="pair">
<div class="spec"><h2>Light (default)</h2><div class="demo">{sw(light, "light")}</div>{rt(light)}</div>
<div class="spec"><h2>Night mode</h2><div class="demo" data-theme="dark">{sw(dark, "dark")}</div>{rt(dark)}</div>
</div>
<div class="spec"><h2>Type: Frank Ruhl Libre for headings, Inter for Latin and figures, Heebo for Hebrew text</h2>
<p class="note">All three are on Google Fonts. Inter has no Hebrew letters, so the stack <code>Inter, Heebo, system-ui</code> gives Hebrew text in Heebo while digits and Latin stay in Inter on both language versions.</p>
<div>{types}</div></div>
<div class="spec"><h2>Shape and space</h2>
<div class="tablewrap"><table class="kv"><tbody>
<tr><td>Radius</td><td><code>--radius: 8px</code> boxes, tables, cards · <code>--radius-sm: 5px</code> tags · 999px chips, badges, switches</td></tr>
<tr><td>Width</td><td><code>--wrap: 1160px</code> with a 24 px gutter (16 px under 640 px)</td></tr>
<tr><td>Breakpoints</td><td>Container queries on <code>.site</code>: 820 px switches the chart variant; 640 px stacks the header and tightens spacing</td></tr>
<tr><td>Rules</td><td>1 px <code>--line</code> inside components; 1 px <code>--line-strong</code> for section tops, table heads and control borders</td></tr>
</tbody></table></div></div>
</div>'''

# ---------- artboard registry ----------
BOARDS = [
    # file, title, kind, lang, theme, width
    ("Main.dc.html", "Benchmarks · EN · desktop · light", "bench", "en", "light", 1280),
    ("Bench-EN-Night.dc.html", "Benchmarks · EN · desktop · night", "bench", "en", "dark", 1280),
    ("Bench-EN-Phone.dc.html", "Benchmarks · EN · 375 · light · 1 of 2", "bench", "en", "light", 375, 1),
    ("Bench-EN-Phone-2.dc.html", "Benchmarks · EN · 375 · light · 2 of 2", "bench", "en", "light", 375, 2),
    ("Bench-EN-Phone-Night.dc.html", "Benchmarks · EN · 375 · night · 1 of 2", "bench", "en", "dark", 375, 1),
    ("Bench-EN-Phone-Night-2.dc.html", "Benchmarks · EN · 375 · night · 2 of 2", "bench", "en", "dark", 375, 2),
    ("Bench-HE.dc.html", "Benchmarks · HE · desktop · light", "bench", "he", "light", 1280),
    ("Bench-HE-Night.dc.html", "Benchmarks · HE · desktop · night", "bench", "he", "dark", 1280),
    ("Bench-HE-Phone.dc.html", "Benchmarks · HE · 375 · light · 1 of 2", "bench", "he", "light", 375, 1),
    ("Bench-HE-Phone-2.dc.html", "Benchmarks · HE · 375 · light · 2 of 2", "bench", "he", "light", 375, 2),
    ("Bench-HE-Phone-Night.dc.html", "Benchmarks · HE · 375 · night · 1 of 2", "bench", "he", "dark", 375, 1),
    ("Bench-HE-Phone-Night-2.dc.html", "Benchmarks · HE · 375 · night · 2 of 2", "bench", "he", "dark", 375, 2),
    ("Home-EN.dc.html", "Home · EN · desktop · light", "home", "en", "light", 1280),
    ("Home-EN-Night.dc.html", "Home · EN · desktop · night", "home", "en", "dark", 1280),
    ("Home-EN-Phone.dc.html", "Home · EN · 375 · light", "home", "en", "light", 375),
    ("Home-HE.dc.html", "Home · HE · desktop · light", "home", "he", "light", 1280),
    ("Chart-Spec.dc.html", "Hero chart specification", "spec", "en", "light", 1400),
    ("Components.dc.html", "Shared components", "components", "en", "light", 1400),
    ("Tokens.dc.html", "Colour and type tokens", "tokens", "en", "light", 1400),
]

def find(kind, lang, theme, w):
    for cand in ((kind, lang, theme, w), (kind, lang, "light", w), (kind, lang, theme, 1280), (kind, lang, "light", 1280)):
        for f, _, k, l, th, ww, *part in BOARDS:
            if (k, l, th, ww) == cand and part != [2]:
                return f
    return "#"

def board_links(kind, lang, theme, w):
    other = "he" if lang == "en" else "en"
    home, bench = find("home", lang, theme, w), find("bench", lang, theme, w)
    m = {"./": home, "benchmarks.html": bench}
    target = find(kind, other, theme, w)
    for href in ("he/benchmarks.html", "../benchmarks.html", "he/", "../"):
        m[href] = target
    return m

def write_canvas(index):
    rows = [  # page id, row title, files
        ("bench", "Benchmarks · English", [f for f in index if f == "Main.dc.html" or f.startswith("Bench-EN")]),
        ("bench", "Benchmarks · עברית", [f for f in index if f.startswith("Bench-HE")]),
        ("home", "Home page · light refresh", [f for f in index if f.startswith("Home")]),
        ("system", "Shared system · chart spec, components, tokens", ["Chart-Spec.dc.html", "Components.dc.html", "Tokens.dc.html"]),
    ]
    boards, notes, y_by_page = {}, {}, {}
    for i, (page, title, files) in enumerate(rows):
        y = y_by_page.get(page, 0)
        x = 0
        for f in files:
            m = index[f]
            b = {"x": x, "y": y, "w": m["w"], "h": m["h"], "title": m["title"], "page": page}
            if m["kind"] in ("bench", "home"):
                b["expand"] = "fill"
                b["is_interactive"] = True
            boards[f] = b
            x += m["w"] + 80
        notes[f"row{i}"] = {"x": 0, "y": y - 300, "text": title, "kind": "title1", "maxW": x - 80, "page": page}
        y_by_page[page] = y + max(index[f]["h"] for f in files) + 520
    canvas = {
        "v": 3,
        "createdOnFiles": {"v": 1, "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "title": "HeOCR Benchmarks redesign",
        "launch": {"view": "canvas", "page": "bench"},
        "pages": [{"id": "bench", "name": "Benchmarks"}, {"id": "home", "name": "Home"}, {"id": "system", "name": "System and specs"}],
        "boards": boards,
        "order": list(boards),
        "notes": notes,
        "designSystems": [],
    }
    (OUT_C / "canvas.json").write_text(json.dumps(canvas, indent=1, ensure_ascii=False), encoding="utf-8")

def build():
    for d in (OUT_H, OUT_H / "he", OUT_T, OUT_C):
        d.mkdir(parents=True, exist_ok=True)
    bad = check_contrast()
    if bad:
        print("CONTRAST FAILURES:\n  " + "\n  ".join(bad))
    # static handoff previews
    for page, lang, path, css in (("bench", "en", "benchmarks.html", "site.css"), ("bench", "he", "he/benchmarks.html", "../site.css"),
                                  ("home", "en", "index.html", "site.css"), ("home", "he", "he/index.html", "../site.css")):
        (OUT_H / path).write_text(static_page(lang, TITLES[(page, lang)], page_body(page, lang, STATIC_TOGGLE), css), encoding="utf-8")
    # artboards + measuring twins
    index = {}
    for f, title, kind, lang, theme, w, *part in BOARDS:
        part = part[0] if part else 0
        h = HEIGHTS.get(f, 4000) + 16
        if kind in ("bench", "home"):
            body, extra, root = page_body(kind, lang, DC_TOGGLE, part), "", f' style="min-height: {h}px"'
            links = board_links(kind, lang, theme, w)
        else:
            body = {"spec": board_chart_spec, "components": board_components, "tokens": board_tokens}[kind]()
            extra, root, links = BOARD_CSS, f' style="width: {w}px; min-height: {h}px"', {}
        (OUT_C / f).write_text(dc_page(lang, title, body, theme, w, h, links, root, extra), encoding="utf-8")
        twin = body.replace(DC_TOGGLE, STATIC_TOGGLE)
        html = static_page(lang, title, twin, "", inline_css=CSS + extra,
                           extra_head='<link rel="stylesheet" href="fonts.css">\n')
        html = html.replace('<html ', f'<html data-theme="{theme}" ', 1)
        (OUT_T / f.replace(".dc.html", ".html")).write_text(html, encoding="utf-8")
        index[f] = {"title": title, "w": w, "h": h, "kind": kind, "lang": lang, "theme": theme}
    (HERE / "boards.json").write_text(json.dumps(index, indent=1, ensure_ascii=False))
    write_canvas(index)
    print("built", len(BOARDS), "boards")

if __name__ == "__main__":
    build()
