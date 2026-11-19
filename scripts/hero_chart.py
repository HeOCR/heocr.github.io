"""Hero chart for the HeOCR Benchmarks page: a static inline SVG built from
results.json (`documents.cells`). Standard library only, no charting library.

    from hero_chart import hero_svg, finding_sentence
    svg_wide   = hero_svg(results["documents"], lang="en", variant="wide")
    svg_narrow = hero_svg(results["documents"], lang="en", variant="narrow")

Emit both variants; site.css shows one of them depending on the container width.
All colour, type and stroke styling lives in site.css (classes hc-*, s-*), so the
same SVG serves light and night mode.

Honesty rules enforced here:
  * every document type in `cells` is drawn, in file order;
  * one linear axis, 0 to 100 %, never truncated or broken;
  * only readers present in the file are drawn; a missing score is a text line,
    never a mark on the axis;
  * the 95 % interval is drawn to scale and also printed as numbers.
"""
from html import escape

ALTERNATIVES = ("docling", "markitdown", "pymupdf4llm")
READER_NAMES = {"heocr": "heocr", "stock": "Tesseract", "docling": "Docling",
                "markitdown": "MarkItDown", "pymupdf4llm": "PyMuPDF4LLM"}
MEASURE = "cer"

# Short chart labels per document type (the long titles stay on the tables).
TYPE_LABELS = {
    "en": {
        "DOCX": "Word (.docx)", "DOC": "legacy Word (.doc)",
        "PDF T1": "correct text layer", "PDF T2": "visual-order text layer",
        "PDF T3": "broken character map", "PDF T4": "scan, wrong OCR layer",
        "PDF T5": "scan, image only", "PDF T6": "text plus text as images",
        "PDF spread": "two pages on one sheet", "Scanned tables": "pages with a ruled table",
    },
    "he": {
        "DOCX": "Word (.docx)\u200e", "DOC": "Word ישן ‏(‎.doc‏)",
        "PDF T1": "שכבת טקסט תקינה",
        "PDF T2": "שכבת טקסט בסדר חזותי",
        "PDF T3": "מפת תווים שבורה",
        "PDF T4": "סריקה עם שכבת OCR שגויה",
        "PDF T5": "סריקה, תמונה בלבד",
        "PDF T6": "טקסט ועוד טקסט כתמונה",
        "PDF spread": "שני עמודים בגיליון אחד",
        "Scanned tables": "עמודים סרוקים עם טבלה",
    },
}

STR = {
    "en": {
        "col_type": "Document type", "col_reader": "Reader", "col_value": "Character error",
        "col_ci": "95% interval",
        "others": "Other open tools",
        "no_alt": "no other open tool reads this format",
        "no_stock": "not scored on this type",
        "no_measure": "no character-error score; see table",
        "aria": "Character error by document type, lower is better. {finding} {gate}"
                "All figures are in the Documents by format tables below.",
        "gate": "The release gate, scored on a fresh set, supports {s} of {n} document types. ",
        "lowest_all": "On the development run, heocr has the lowest character error on all {m} document types that another tool also reads",
        "lowest_some": "On the development run, heocr has the lowest character error on {k} of the {m} document types that another tool also reads",
        "clear_all": ", with no overlap between 95% intervals.",
        "clear_some": "; its 95% interval is clear of every other reader on {c} of them.",
        "behind": " It is not the lowest on: {types}.",
        "only": " {types} is read by heocr alone.",
        "list_sep": ", ",
    },
    "he": {
        "col_type": "סוג מסמך", "col_reader": "קורא",
        "col_value": "שגיאת תווים",
        "col_ci": "רווח סמך 95%",
        "others": "כלים פתוחים אחרים",
        "no_alt": "אף כלי פתוח אחר לא קורא את הפורמט הזה",
        "no_stock": "לא הוערך על סוג זה",
        "no_measure": "אין ציון שגיאת תווים; ראו בטבלה",
        "aria": "שגיאת תווים לפי סוג מסמך, נמוך יותר עדיף. {finding} {gate}"
                "כל המספרים מופיעים בטבלאות של מסמכים לפי פורמט למטה.",
        "gate": "שער השחרור, שהוערך על קבוצה חדשה, תומך ב־{s} מתוך {n} סוגי מסמכים. ",
        "lowest_all": "בהרצת הפיתוח, ל־‎heocr‏ שגיאת התווים הנמוכה ביותר בכל {m} סוגי המסמכים שגם כלי אחר קורא",
        "lowest_some": "בהרצת הפיתוח, ל־‎heocr‏ שגיאת התווים הנמוכה ביותר ב־{k} מתוך {m} סוגי המסמכים שגם כלי אחר קורא",
        "clear_all": ", בלי חפיפה בין רווחי הסמך של 95%.",
        "clear_some": "; ב־{c} מהם רווח הסמך שלו אינו חופף לאף קורא אחר.",
        "behind": " הוא אינו הנמוך ביותר ב: {types}.",
        "only": " את {types} קורא רק heocr.",
        "list_sep": ", ",
    },
}

GEOM = {
    # all numbers are SVG user units; at 1:1 they are CSS px
    "wide": dict(W=880, TOP=26, GH=70, PAD=8, ROW=18, HEAD=0, P0=196, PW=400,
                 NAME=626, VAL=796, VAL_W=50, CI=880, CI_W=72, TICKS=(0, 25, 50, 75, 100),
                 BAR_OURS=8, BAR=5, R=5, SQ=8, DIA=6, CAP=4.5),
    "narrow": dict(W=360, TOP=20, GH=96, PAD=0, ROW=20, HEAD=28, P0=110, PW=124,
                   NAME=0, VAL=290, VAL_W=46, CI=360, CI_W=62, TICKS=(0, 50, 100),
                   BAR_OURS=7, BAR=4, R=4.5, SQ=7, DIA=5.5, CAP=4),
}


def fmt(x):
    """Same rule as the tables: two decimals under 1 %, otherwise one."""
    return f"{x * 100:.2f}" if x < 0.01 else f"{x * 100:.1f}"


def pct(x):
    return fmt(x) + "%"


def interval(ci):
    return f"{fmt(ci[0])}–{fmt(ci[1])}"


def chart_rows(doc):
    """One entry per document type: heocr, the best alternative, stock Tesseract."""
    out = []
    for code, cell in doc["cells"].items():
        readers = cell["readers"]
        scored = [(k, readers[k][MEASURE]) for k in ALTERNATIVES if MEASURE in readers.get(k, {})]
        best = min(scored, key=lambda kv: kv[1]["value"]) if scored else None
        stock = readers.get("stock")
        out.append({
            "code": code, "n": cell["documents"],
            "ours": ("heocr", readers["heocr"][MEASURE]),
            "alt": best,
            "tess": ("stock", stock[MEASURE]) if stock and MEASURE in stock else None,
            "tess_reason": None if stock and MEASURE in stock else ("no_measure" if stock else "no_stock"),
        })
    return out


def finding(doc):
    """Counts behind the headline sentence; every reader in a cell is compared."""
    k = m = clear = 0
    behind, only = [], []
    for code, cell in doc["cells"].items():
        ours = cell["readers"]["heocr"][MEASURE]
        others = [r[MEASURE] for name, r in cell["readers"].items() if name != "heocr" and MEASURE in r]
        if not others:
            only.append(code)
            continue
        m += 1
        if ours["value"] < min(o["value"] for o in others):
            k += 1
            if ours["ci95"][1] < min(o["ci95"][0] for o in others):
                clear += 1
        else:
            behind.append(code)
    return {"lowest": k, "comparable": m, "clear": clear, "behind": behind, "only": only}


def finding_sentence(doc, lang="en"):
    s, f = STR[lang], finding(doc)
    k, m = f["lowest"], f["comparable"]
    text = (s["lowest_all"] if k == m else s["lowest_some"]).format(k=k, m=m)
    if doc.get("heldout"):  # the figures come from a registered held-out run, not the development run
        text = text.replace("On the development run", "On the held-out set").replace("בהרצת הפיתוח", "בקבוצה המוחזקת בצד")
    text += s["clear_all"] if f["clear"] == k else s["clear_some"].format(c=f["clear"])
    if f["behind"]:
        text += s["behind"].format(types=s["list_sep"].join(f["behind"]))
    if f["only"]:
        text += s["only"].format(types=s["list_sep"].join(f["only"]))
    return text


def _is_rtl(text):
    return any("֐" <= ch <= "׿" for ch in text)


def hero_svg(doc, lang="en", variant="wide"):
    g, s, labels = GEOM[variant], STR[lang], TYPE_LABELS[lang]
    rtl_page = lang == "he"
    W = g["W"]
    rows = chart_rows(doc)
    H = g["TOP"] + len(rows) * g["GH"] + 6
    o = []

    def mx(x):
        return W - x if rtl_page else x

    def num(v):
        return f"{v:.1f}".rstrip("0").rstrip(".")

    def text(x, y, content, cls, edge="start", raw=False):
        """edge: which page-relative edge of the text sits at x (start, end or mid)."""
        d = "rtl" if _is_rtl(content) else "ltr"
        if edge == "mid":
            anchor = "a-m"
        else:
            left = (edge == "start") != rtl_page
            anchor = "a-s" if left == (d == "ltr") else "a-e"
        body = content if raw else escape(content)
        o.append(f'<text x="{num(mx(x))}" y="{num(y)}" class="{cls} {anchor} d-{d}">{body}</text>')

    def number(x_end, width, y, content, cls):
        """Numbers stay right-aligned in their slot in both page directions."""
        right = x_end if not rtl_page else (W - x_end) + width
        o.append(f'<text x="{num(right)}" y="{num(y)}" class="{cls} a-e d-ltr">{escape(content)}</text>')

    def xval(v):
        return g["P0"] + min(max(v, 0.0), 1.0) * g["PW"]

    def hline(x1, x2, y, cls):
        o.append(f'<line x1="{num(mx(x1))}" y1="{num(y)}" x2="{num(mx(x2))}" y2="{num(y)}" class="{cls}"></line>')

    def vline(x, y1, y2, cls):
        o.append(f'<line x1="{num(mx(x))}" y1="{num(y1)}" x2="{num(mx(x))}" y2="{num(y2)}" class="{cls}"></line>')

    def series(key, entry, yc):
        name, m = entry
        v, (lo, hi) = m["value"], m["ci95"]
        ours = key == "ours"
        bar_h = g["BAR_OURS"] if ours else g["BAR"]
        x0, xv = g["P0"], xval(v)
        left = min(mx(x0), mx(xv))
        o.append(f'<g class="s-{key}">')
        o.append(f'<rect x="{num(left)}" y="{num(yc - bar_h / 2)}" width="{num(abs(xv - x0))}" height="{num(bar_h)}" class="hc-bar"></rect>')
        cap = g["CAP"] + (1 if ours else 0)
        hline(xval(lo), xval(hi), yc, "hc-ci")
        vline(xval(lo), yc - cap, yc + cap, "hc-ci")
        vline(xval(hi), yc - cap, yc + cap, "hc-ci")
        cx = mx(xv)
        if key == "ours":
            o.append(f'<circle cx="{num(cx)}" cy="{num(yc)}" r="{num(g["R"])}" class="hc-mark"></circle>')
        elif key == "alt":
            q = g["SQ"]
            o.append(f'<rect x="{num(cx - q / 2)}" y="{num(yc - q / 2)}" width="{num(q)}" height="{num(q)}" class="hc-mark hollow"></rect>')
        else:
            d = g["DIA"]
            pts = f"{num(cx)},{num(yc - d)} {num(cx + d)},{num(yc)} {num(cx)},{num(yc + d)} {num(cx - d)},{num(yc)}"
            o.append(f'<polygon points="{pts}" class="hc-mark"></polygon>')
        o.append("</g>")
        return v, lo, hi

    v = [c.get("verdict") for c in doc["cells"].values()]
    gate = "" if doc.get("gate", "not_run") == "not_run" else s["gate"].format(s=v.count("supported"), n=len(v))
    aria = s["aria"].format(finding=finding_sentence(doc, lang), gate=gate)
    o.append(f'<svg class="hc hc-{variant}" viewBox="0 0 {W} {num(H)}" role="img" aria-label="{escape(aria, quote=True)}">')

    # axis header
    ty = g["TOP"] - 10
    for t in g["TICKS"]:
        text(g["P0"] + t / 100 * g["PW"], ty, f"{t}%" if t == 100 else str(t), "hc-tick", "mid")
    if variant == "wide":
        text(0, ty, s["col_type"], "hc-colh")
        text(g["NAME"], ty, s["col_reader"], "hc-colh")
        text(g["VAL"], ty, s["col_value"], "hc-colh", "end")
        text(g["CI"], ty, s["col_ci"], "hc-colh", "end")
    hline(0, W, g["TOP"], "hc-rule")

    for i, r in enumerate(rows):
        gy = g["TOP"] + i * g["GH"]
        o.append('<g class="hc-g">')
        o.append(f'<rect x="0" y="{num(gy)}" width="{W}" height="{g["GH"]}" class="hc-hit"></rect>')
        if i:
            hline(0, W, gy, "hc-sep")
        r0 = gy + g["PAD"] + g["HEAD"]          # top of the three series rows
        base = [r0 + g["ROW"] * k + g["ROW"] / 2 + 4.5 for k in range(3)]
        n_label = f"n = {r['n']}"
        if variant == "wide":
            text(0, base[0], r["code"], "hc-type")
            text(0, base[1], labels[r["code"]], "hc-desc")
            text(0, base[2], n_label, "hc-n")
        else:
            gap = ("\u200f" if rtl_page else "") + "\u00a0\u00a0"   # RLM keeps the Latin code at the start edge
            head = f'{escape(r["code"])}{gap}<tspan class="hc-desc">{escape(labels[r["code"]])}</tspan>'
            o.append(f'<text x="{num(mx(0))}" y="{num(gy + 19)}" class="hc-type a-s d-{"rtl" if rtl_page else "ltr"}">{head}</text>')
            text(W, gy + 19, n_label, "hc-n", "end")

        slots = (("ours", r["ours"]), ("alt", r["alt"]), ("tess", r["tess"]))
        for k, (key, entry) in enumerate(slots):
            yc = r0 + g["ROW"] * k + g["ROW"] / 2
            for t in g["TICKS"]:        # gridlines only behind real marks; the zero line always
                if t == 0 or entry is not None:
                    vline(g["P0"] + t / 100 * g["PW"], yc - g["ROW"] / 2, yc + g["ROW"] / 2, "hc-zero" if t == 0 else "hc-grid")
            if entry is None:
                label = s["others"] if key == "alt" else READER_NAMES["stock"]
                reason = s["no_alt"] if key == "alt" else s[r["tess_reason"]]
                text(g["NAME"], base[k], label, "hc-name none")
                text(g["P0"] + 8, base[k], reason, "hc-miss")
                if variant == "wide":
                    number(g["VAL"], g["VAL_W"], base[k], "–", "hc-val none")
                continue
            name, m = entry
            series(key, entry, yc)
            label = READER_NAMES[name]
            if m.get("n") is not None and m["n"] != r["n"]:
                label += f" (n={m['n']})"
            cls = " ours" if key == "ours" else ""
            text(g["NAME"], base[k], label, "hc-name" + cls)
            number(g["VAL"], g["VAL_W"], base[k], pct(m["value"]), "hc-val" + cls)
            number(g["CI"], g["CI_W"], base[k], interval(m["ci95"]), "hc-civ")
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)


def legend_marker(key):
    """The same marks, for the HTML legend (14 x 14)."""
    shape = {
        "ours": '<circle cx="7" cy="7" r="5" class="hc-mark"></circle>',
        "alt": '<rect x="3" y="3" width="8" height="8" class="hc-mark hollow"></rect>',
        "tess": '<polygon points="7,1 13,7 7,13 1,7" class="hc-mark"></polygon>',
    }[key]
    return f'<svg viewBox="0 0 14 14" class="s-{key}" aria-hidden="true">{shape}</svg>'


if __name__ == "__main__":
    import json
    import sys
    results = json.load(open(sys.argv[1], encoding="utf-8"))
    lang = sys.argv[2] if len(sys.argv) > 2 else "en"
    variant = sys.argv[3] if len(sys.argv) > 3 else "wide"
    sys.stdout.write(hero_svg(results["documents"], lang, variant))
