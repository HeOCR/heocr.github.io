"""Brand stage for direction B (Bounding Box): logo options, palette + type, design language."""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], "/mnt/user-data/uploads/heocr-site-design-pack/current"]
import build as B          # noqa: E402

base = (HERE / "handoff/site.css").read_text(encoding="utf-8")
a, b = base.index("/* ---------- 1. Tokens"), base.index("/* ---------- 2. Base")
CSS_B = base[:a] + (HERE / "brand_b.css").read_text(encoding="utf-8") + "\n" + base[b:] + (HERE / "brand_b_layer.css").read_text(encoding="utf-8")
(HERE / "site_b.css").write_text(CSS_B, encoding="utf-8")
B.CSS = CSS_B
B.FONTS = "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+Hebrew:wght@400;500;700;800&display=swap"

OUT_C = HERE.parent / "canvas" / "project"
OUT_T = HERE / "twins"
HEIGHTS = json.loads((HERE / "brand_heights.json").read_text()) if (HERE / "brand_heights.json").exists() else {}

H = '<rect x="{x}" y="{y}" width="{s}" height="{s}" class="lg-h"></rect>'
MARKS = {
    1: ('<rect x="7" y="7" width="34" height="34" class="lg-box sw2"></rect>'
        + "".join(H.format(x=x, y=y, s=6) for x, y in ((4, 4), (38, 4), (4, 38), (38, 38)))
        + '<path d="M16 18H32V32.5" class="lg-ink sw45"></path><path d="M16 24.5V32.5" class="lg-ink sw45"></path>'),
    2: ('<path d="M5 14.5V5H14.5" class="lg-box sw3"></path><path d="M33.5 5H43V14.5" class="lg-box sw3"></path>'
        '<path d="M43 33.5V43H33.5" class="lg-box sw3"></path><path d="M14.5 43H5V33.5" class="lg-box sw3"></path>'
        '<path d="M13.5 15.5H34.5V36" class="lg-ink sw55"></path><path d="M13.5 24V36" class="lg-ink sw55"></path>'),
    3: ('<path d="M9 11H39V39" class="lg-ink sw5"></path><path d="M9 21V39" class="lg-ink sw5"></path>'
        + "".join(H.format(x=x, y=y, s=8) for x, y in ((5, 7), (35, 7), (35, 35), (5, 35)))),
}
NAMES = {1: "Boxed", 2: "Corners", 3: "Letter as box"}
LINES = {
    1: "The letter ה inside a detection box with four handles. Closest to the direction board.",
    2: "Viewfinder corners only. Lighter, and the letter can be larger at small sizes.",
    3: "The three strokes of ה are the box, and the handles sit on its corners. Letter and idea are one shape.",
}
DEFAULT = 3


def mark(n, px=None):
    style = f' style="width: {px}px; height: {px}px"' if px else ''
    return f'<svg viewBox="0 0 48 48" aria-hidden="true"{style}>{MARKS[n]}</svg>'


def lockup(n, px, sub=None, rtl=False):
    small = f'<small lang="he" dir="rtl">{sub}</small>' if sub else ''
    word = f'<span dir="ltr">He<b>OCR</b>{small}</span>'
    return f'<span class="lockup" style="font-size: {px}px"{" dir=\"rtl\"" if rtl else ""}>{mark(n)}{word}</span>'


EXTRA_CSS = B.BOARD_CSS + '''
.lg-col{display:flex;flex-direction:column;gap:14px}
.lg-col h2{font-size:1.25rem}
.lg-stage{border:1px solid var(--line);background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;padding:44px 20px 36px}
.lg-tile{border:1px solid var(--line);background:var(--bg);color:var(--text);min-height:92px;display:flex;align-items:center;justify-content:center;gap:26px;padding:16px}
.lg-sizes{align-items:flex-end}
.lg-sizes span{display:flex;flex-direction:column;align-items:center;gap:8px;font:500 .68rem/1 var(--font-mono);color:var(--muted)}
.lg-tagged{position:relative;display:inline-flex;margin-top:18px}
.lg-tagged i{position:absolute;inset-inline-start:0;bottom:100%;font:700 .68rem/1 var(--font-mono);font-style:normal;background:var(--accent);color:var(--on-accent);padding:4px 7px;white-space:nowrap}
.motif{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.motif .demo{min-height:190px;justify-content:center;padding:44px 34px 30px}
.motif h3{font:700 1.7rem/1.1 var(--font-display);letter-spacing:-.035em;display:inline-block;align-self:flex-start}
.rules{columns:2;column-gap:40px;margin:0;padding-inline-start:20px;font-size:.92rem}
.rules li{margin:0 0 6px;break-inside:avoid}
'''


def board_logo():
    cols = []
    for n in (1, 2, 3):
        cols.append(f'''<div class="lg-col">
<h2>Logo {n} · {NAMES[n]}</h2>
<p class="note" style="min-height: 3.2em; margin: 0">{LINES[n]}</p>
<div class="lg-stage">{mark(n, 132)}{lockup(n, 40)}</div>
<div class="lg-tile lg-sizes"><span>{mark(n, 64)}64</span><span>{mark(n, 32)}32</span><span>{mark(n, 24)}24</span><span>{mark(n, 16)}16</span></div>
<div class="lg-tile" data-theme="dark">{lockup(n, 30)}{mark(n, 24)}</div>
<div class="lg-tile">{lockup(n, 30, sub="זיהוי טקסט עברי, פתוח לכולם", rtl=True)}</div>
<div class="lg-tile gridband"><span class="lg-tagged"><i>ה 0.99</i>{mark(n, 72)}</span>{lockup(n, 26).replace("He<b>OCR</b>", "he<b>ocr</b>")}</div>
</div>''')
    return f'''<div class="sheet">
<div><h1 class="sheet-title">Logo: three refinements</h1>
<p class="sheet-lede">All three are the letter ה, drawn on a 48-unit grid from three straight strokes, plus the detection-box idea. Each column shows the mark, the lockup, small sizes down to a 16 px favicon, night mode, the Hebrew lockup, and two extras: the mark with a confidence tag, and a lowercase wordmark matching the package name.</p></div>
<div class="trio">{"".join(cols)}</div>
</div>'''


def board_palette():
    light, dark = B.tokens()
    names = ["bg", "surface", "tag", "accent-soft", "line", "line-strong", "grid", "text", "muted", "accent", "on-accent",
             "series-ours", "series-alt", "series-tess", "ok", "ok-soft", "no", "no-soft"]
    kept = {"bg", "surface", "text", "muted", "line", "tag"}

    def sw(tk, theme):
        out = []
        for n in names:
            note = "today's value" if (theme == "dark" and n in kept) else ""
            out.append(f'<div class="swatch"><i style="background:var(--{n})"></i><div><b>--{n}</b>{tk[n]}<br><span>{note or "&nbsp;"}</span></div></div>')
        return '<div class="swatches">' + "".join(out) + '</div>'

    def ratios(tk):
        return "".join(f'<tr><td><code>--{fg}</code> on <code>--{bg}</code></td><td class="num">{B.contrast(tk[fg], tk[bg]):.1f}:1</td><td class="num">{need}:1</td></tr>'
                       for fg, bg, need in B.PAIRS)
    rt = lambda tk: f'<div class="tablewrap"><table class="kv"><thead><tr><th>Pair</th><th>Contrast</th><th>Needed</th></tr></thead><tbody>{ratios(tk)}</tbody></table></div>'

    def trow(label, style, en, he):
        return (f'<div class="type-row"><p class="spec-label">{label}</p><div style="{style}">{en}</div>'
                f'<div style="{style}" dir="rtl" lang="he">{he}</div></div>')
    types = (
        trow("h1 · JetBrains Mono 700<br>Hebrew: Noto Sans Hebrew 700", "font:700 2.9rem/1.1 var(--font-display);letter-spacing:-.035em", "HeOCR benchmarks", "מדדי ביצועים של HeOCR")
        + trow("h2 · 1.45rem", "font:700 1.45rem/1.2 var(--font-display);letter-spacing:-.035em", "Documents by format", "מסמכים לפי פורמט")
        + trow("h3 · Noto Sans Hebrew 700<br>1.02rem", "font:700 1.02rem/1.35 var(--font-body)", "PDF with a correct text layer", "PDF עם שכבת טקסט תקינה")
        + trow("Lede · 1.1rem / 1.6", "font:400 1.1rem/1.6 var(--font-body)", "How HeOCR compares with other open tools, per kind of document.", "איך HeOCR משתווה לכלים פתוחים אחרים, לפי סוג המסמך.")
        + trow("Body · 1rem / 1.6", "font:400 1rem/1.6 var(--font-body)", "Each table is one kind of document.", "כל טבלה היא סוג מסמך אחד.")
        + trow("Label · JetBrains Mono 500<br>0.76rem", "font:500 .76rem/1.5 var(--font-mono);color:var(--muted)", "lower is better · n = 318", "נמוך יותר עדיף · <bdi dir=\"ltr\">n = 318</bdi>")
        + trow("Figures · JetBrains Mono 700", "font:700 .95rem/1.6 var(--font-mono)", "0.27%  22.1%  100.0%", "<bdi dir=\"ltr\">0.27%  22.1%  100.0%</bdi>")
        + trow("Tag · JetBrains Mono 700<br>0.68rem on accent", "font:700 .68rem/1 var(--font-mono)", '<span style="background:var(--accent);color:var(--on-accent);padding:4px 7px">figure · hero</span>', '<span style="background:var(--accent);color:var(--on-accent);padding:4px 7px">איור · ראשי</span>'))
    return f'''<div class="sheet">
<div><h1 class="sheet-title">Palette and type</h1>
<p class="sheet-lede">One brand colour, detection blue, on a white ground. Green and red are reserved for data: heocr and the best other tool in the chart, and the two verdicts. Night mode keeps today's six neutral values; only the accent changes, to the brand blue lifted for a dark ground.</p></div>
<div class="pair">
<div class="spec"><h2>Light (default)</h2><div class="demo">{sw(light, "light")}</div>{rt(light)}</div>
<div class="spec"><h2>Night mode</h2><div class="demo" data-theme="dark">{sw(dark, "dark")}</div>{rt(dark)}</div>
</div>
<div class="spec"><h2>Type: JetBrains Mono for headings, labels and figures; Noto Sans Hebrew for text and all Hebrew</h2>
<p class="note">Both are on Google Fonts. JetBrains Mono has no Hebrew letters, so Hebrew headings fall to Noto Sans Hebrew at the same weight, while identifiers, tags and numbers stay monospace on both language versions.</p>
<div>{types}</div></div>
</div>'''


def board_language():
    body = B.board_components()
    brand = f'{mark(DEFAULT)}<span dir="ltr">He<b>OCR</b></span>'
    body = body.replace('>HeOCR</a>', f'>{brand}</a>')
    body = body.replace('<div class="foot-brand">HeOCR</div>', '<div class="foot-brand">He<b style="color:var(--accent)">OCR</b></div>')
    body = body.replace('<h1 class="sheet-title">Shared components</h1>', '<h1 class="sheet-title">Design language</h1>')
    body = re.sub(r'<p class="sheet-lede">.*?</p>',
                  '<p class="sheet-lede">The site speaks the language of OCR output. A blue box with four handles marks a detected region; a small monospace tag names it. Everything else stays quiet: white ground, square corners, hairlines.</p>', body, count=1, flags=re.S)
    body = body.replace('the current page is underlined', 'the current page is bracketed')
    old = B.section(B.OLD[("bench", "en")], "p-mod")
    empty = '<div class="empty">' + B.one(r'<div class="empty">(.*?)</div>', old) + '</div>'
    doc = B.sample_doc(["PDF T1", "DOC"])
    motif = f'''<div class="spec"><h2>The box</h2>
<div class="motif">
<div class="demo gridband"><h3 class="bb" data-tag="h1 · 0.99">HeOCR benchmarks</h3></div>
<div class="demo gridband" dir="rtl" lang="he"><h3 class="bb" data-tag="h1 · 0.99">מדדי ביצועים</h3></div>
<div class="demo gridband" data-theme="dark"><h3 class="bb" data-tag="h1 · 0.99">HeOCR benchmarks</h3></div>
</div>
<ul class="rules">
<li><strong>What gets a box:</strong> the logo, the page title, the hero figure, and the “ours” rows in tables (as two blue rules). Nothing else.</li>
<li><strong>Anatomy:</strong> 1.5 px outline in <code>--accent</code>, 8 px offset, four 8 px square handles centred on the corners.</li>
<li><strong>Tag:</strong> optional, on the start side above the box: JetBrains Mono 700, 0.68rem, on <code>--accent</code>. It names the region (<code>h1</code>, <code>figure · hero</code>); the number is decorative on the title only.</li>
<li><strong>Grid:</strong> a 28 px hairline grid in <code>--grid</code> sits behind the page head only, never behind text blocks or tables.</li>
<li><strong>Shape:</strong> square corners everywhere (2 px radius), 1 px hairlines, no shadows, no gradients.</li>
<li><strong>Colour:</strong> blue is the brand and the interface. Green and red appear only in the chart and the verdict badges.</li>
<li><strong>Hebrew:</strong> the layout mirrors, the tag moves to the right-hand corner, numbers and identifiers stay left-to-right.</li>
<li><strong>Navigation:</strong> the current page is bracketed, <code>[Benchmarks]</code>, in blue.</li>
</ul>
<p class="spec-label">Hero figure as one detected region, with its tag (excerpt of the real chart)</p>
<div class="demo" style="padding: 40px 34px 30px"><figure class="hero-chart" style="margin: 0"><div class="panel hc-demo-wide" data-tag="figure · hero">
<div class="hc-title"><h2>Character error by document type</h2><span class="dir">lower is better</span></div>
{B.legend("en")}
{B.hc.hero_svg(doc, "en", "wide")}
</div></figure></div>
</div>
'''
    i = body.index('<div class="spec">')
    return body[:i] + motif + body[i:]


BOARDS = [
    ("Brand-Logo.dc.html", "Brand B · Logo options", board_logo, 1440),
    ("Brand-Palette-Type.dc.html", "Brand B · Palette and type", board_palette, 1400),
    ("Brand-Language.dc.html", "Brand B · Design language", board_language, 1400),
]

if __name__ == "__main__":
    bad = B.check_contrast()
    print("contrast:", bad or "all pass")
    out = {}
    for f, title, fn, w in BOARDS:
        h = HEIGHTS.get(f, 3000) + 16
        body = fn()
        root = f' style="width: {w}px; min-height: {h}px"'
        (OUT_C / f).write_text(B.dc_page("en", title, body, "light", w, h, {}, root, EXTRA_CSS), encoding="utf-8")
        twin = body.replace(B.DC_TOGGLE, B.STATIC_TOGGLE)
        html = B.static_page("en", title, twin, "", inline_css=CSS_B + EXTRA_CSS, extra_head='<link rel="stylesheet" href="dfonts.css">\n')
        (OUT_T / f.replace(".dc.html", ".html")).write_text(html, encoding="utf-8")
        out[f] = {"w": w, "h": h, "title": title}
    (HERE / "brand_boards.json").write_text(json.dumps(out, indent=1))
    print("built", len(out))
