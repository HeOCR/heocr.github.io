"""Full site in the Bounding Box brand: Benchmarks, home, htext (static handoff + canvas artboards)."""
import json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
import brand as BR         # noqa: E402  (imports build, swaps in the Bounding Box tokens and fonts)
B = BR.B
SRC = Path("/mnt/user-data/uploads/heocr-site-design-pack/current")
SRC2 = HERE / "src2"                       # pages attached later: newer htext, Hebrew htext, rights
B.OLD[("htext", "en")] = (SRC2 / "htext.html").read_text(encoding="utf-8")
B.OLD[("htext", "he")] = (SRC2 / "htext_he.html").read_text(encoding="utf-8")
B.OLD[("rights", "en")] = (SRC2 / "rights.html").read_text(encoding="utf-8")
B.OLD[("rights", "he")] = (SRC2 / "rights_he.html").read_text(encoding="utf-8")
LOGO = 1

PAGE_CSS = '''
/* ---------- 13. Page pieces in the Bounding Box language ---------- */
.band { border-bottom: 1px solid var(--line); }
.band .page-head { padding-block: 58px 30px; }
.page-head h1 { margin: 0 0 28px; }
.bb { display: inline-block; }
.home-hero { padding-block: 64px 44px; }
.home-hero h1 { font-size: clamp(2.3rem, 1.6rem + 3.4cqi, 3.4rem); margin: 34px 0 28px; }
.he, .tag { font-family: var(--font-body); font-weight: 500; }
.site main.home section > h2, main.doc section > h2 { padding-top: 22px; border-top: 1px solid var(--line-strong); margin: 0 0 12px; }
.card, .tablewrap, .method, .toc, .gate-summary { border-radius: 2px; }
.flow .step { font-family: var(--font-mono); font-size: 0.8rem; }
/* document pages (htext, rights) */
main.doc p, main.doc li { max-width: 48em; }
main.doc li { margin: 0 0 8px; }
main.doc li > ul { margin-top: 8px; }
main.doc:not(.ht) > section { max-width: 780px; }
main.doc .status { margin: 0 6px 10px 0; margin-inline: 0 6px; }
main.doc .facts { padding: 4px 0; padding-inline-start: 20px; font-size: 0.9rem; }
main.doc td, main.doc th { vertical-align: top; }
tr.total td { font-weight: 700; }
.stats { display: flex; flex-wrap: wrap; gap: 12px; margin: 14px 0 4px; }
.stat { border: 1px solid var(--line); background: var(--bg); padding: 12px 16px; min-width: 150px; }
.stat b { display: block; font: 700 1.35rem/1.25 var(--font-mono); letter-spacing: -0.03em; }
.stat > span { color: var(--muted); font-size: 0.85rem; }
pre { background: var(--surface); border: 1px solid var(--line); border-radius: 2px; padding: 12px 14px; overflow-x: auto; font-size: 0.82rem; direction: ltr; text-align: left; }
pre code { background: none; padding: 0; white-space: pre; }
.credit { border: 1px solid var(--line); background: var(--surface); padding: 10px 14px; }
@container site (max-width: 820px) {
  .hc-narrow text { font-size: 11.5px; }
  .hc-narrow .hc-name { font-size: 10.5px; }
  .hc-narrow .hc-civ, .hc-narrow .hc-tick { font-size: 10px; }
}
@container site (max-width: 640px) {
  .band .page-head { padding-block: 46px 22px; }
  .hero-chart .panel { border: 0; border-top: 1.5px solid var(--accent); }
  .hero-chart .panel::after, .hero-chart .panel[data-tag]::before { display: none; }
  .home-hero { padding-block: 44px 30px; }
}
'''
B.CSS = B.CSS + PAGE_CSS
TAG_H1 = "h1 · 0.99"


def brand_link(href):
    return f'<a class="brand" href="{href}" aria-label="HeOCR">{BR.mark(LOGO)}<span dir="ltr">He<b>OCR</b></span></a>'


def header(lang, page, toggle, home_href="./"):
    t = B.T[lang]
    lt = B.one(r'<div class="lang-toggle">(.*?)</div>', B.OLD[(page, lang)]).strip()
    cur = ' aria-current="page"'
    nav = (f'<a href="benchmarks.html"{cur if page == "bench" else ""}>{t["nav_bench"]}</a>'
           f'<a href="htext.html"{cur if page == "htext" else ""}>{t["nav_htext"]}</a>'
           f'<a href="rights.html"{cur if page == "rights" else ""}>{t["nav_rights"]}</a>')
    return f'''<a class="skip" href="#main">{t["skip"]}</a>
<header class="site-header">
<div class="wrap bar">
{brand_link(home_href)}
<nav class="site-nav" aria-label="{t["nav_aria"]}">{nav}</nav>
<div class="tools">
<div class="lang-toggle" role="group" aria-label="{t["lang_aria"]}">
{lt}
</div>
<button class="theme-toggle" type="button" {toggle}>{B.ICON["moon"]}{B.ICON["sun"]}<span class="label">{t["theme"]}</span></button>
</div>
</div>
</header>'''


_footer = B.footer
def footer(lang, page):
    return _footer(lang, page).replace('<div class="foot-brand">HeOCR</div>', '<div class="foot-brand">He<b>OCR</b></div>')


def boxed(inner):
    return f'<span class="bb" data-tag="{TAG_H1}">{inner}</span>'


_bench = B.bench_main
def bench_main(lang, part=0):
    s = _bench(lang, part)
    s = re.sub(r'<div class="wrap page-head">\n<h1>(.*?)</h1>(.*?)</div>\n<figure',
               lambda m: f'<div class="band gridband"><div class="wrap page-head">\n<h1>{boxed(m.group(1))}</h1>{m.group(2)}</div></div>\n<figure', s, count=1, flags=re.S)
    return s.replace('<div class="panel">', '<div class="panel" data-tag="figure · hero">')


_home = B.home_main
def home_main(lang):
    s = _home(lang).replace('<div class="home-hero">', '<div class="home-hero band gridband">', 1)
    return re.sub(r'<h1>(.*?)</h1>', lambda m: f'<h1>{boxed(m.group(1))}</h1>', s, count=1)


def htext_main(lang="en"):
    old = B.OLD[("htext", lang)]
    head = B.one(r'<header>(.*?)</header>', old)
    h1 = B.one(r'<h1>(.*?)</h1>', head)
    lede = B.one(r'(<p class="lede">.*?</p>)', head)
    note = B.one(r'(<p class="note">.*?</p>)', head)
    main = B.one(r'<main class="wrap doc ht">(.*?)</main>', old)
    toc = B.every(r'(<a href="#[\w-]+">.*?</a>)', B.one(r'<nav class="toc">(.*?)</nav>', main))
    main = re.sub(r'<nav class="toc">.*?</nav>', '', main, count=1, flags=re.S)
    return f'''<div class="band gridband"><div class="wrap page-head">
<h1>{boxed(h1)}</h1>
{lede}
{note}
</div></div>
<nav class="wrap" aria-label="{B.T[lang]["toc_aria"]}"><div class="toc">{"".join(toc)}</div></nav>
<main id="main" class="wrap doc ht">{main}</main>'''


def rights_main(lang="en"):
    old = B.OLD[("rights", lang)]
    head = B.one(r'<header>(.*?)</header>', old)
    main = B.one(r'<main class="wrap doc">(.*?)</main>', old)
    return f'''<div class="band gridband"><div class="wrap page-head">
<h1>{boxed(B.one(r'<h1>(.*?)</h1>', head))}</h1>
{B.one(r'(<p class="lede">.*?</p>)', head)}
</div></div>
<main id="main" class="wrap doc">{main}</main>'''


B.header, B.footer, B.bench_main, B.home_main = header, footer, bench_main, home_main
for _k in (("htext", "en"), ("htext", "he"), ("rights", "en"), ("rights", "he")):
    B.TITLES[_k] = B.one(r'<title>(.*?)</title>', B.OLD[_k])


def page_body(page, lang, toggle, part=0):
    if page in ("htext", "rights"):
        main = htext_main(lang) if page == "htext" else rights_main(lang)
        return header(lang, page, toggle) + "\n" + main + "\n" + footer(lang, page)
    return B.page_body(page, lang, toggle, part)


BOARDS = [b for b in B.BOARDS if b[2] in ("bench", "home")] + [
    ("Htext-EN.dc.html", "htext · EN · desktop · light", "htext", "en", "light", 1280),
    ("Htext-EN-Night.dc.html", "htext · EN · desktop · night", "htext", "en", "dark", 1280),
    ("Htext-EN-Phone.dc.html", "htext · EN · 375 · light", "htext", "en", "light", 375),
    ("Htext-HE.dc.html", "htext · HE · desktop · light", "htext", "he", "light", 1280),
    ("Rights-EN.dc.html", "Rights · EN · desktop · light", "rights", "en", "light", 1280),
    ("Rights-EN-Night.dc.html", "Rights · EN · desktop · night", "rights", "en", "dark", 1280),
    ("Rights-EN-Phone.dc.html", "Rights · EN · 375 · light", "rights", "en", "light", 375),
    ("Rights-HE.dc.html", "Rights · HE · desktop · light", "rights", "he", "light", 1280),
    ("Chart-Spec.dc.html", "Brand B · Hero chart specification", "spec", "en", "light", 1400),
    ("Brand-Logo.dc.html", "Brand B · Logo options", "logo", "en", "light", 1440),
    ("Brand-Palette-Type.dc.html", "Brand B · Palette and type", "palette", "en", "light", 1400),
    ("Brand-Language.dc.html", "Brand B · Design language", "language", "en", "light", 1400),
]


def find(kind, lang, theme, w):
    for cand in ((kind, lang, theme, w), (kind, lang, "light", w), (kind, lang, theme, 1280), (kind, lang, "light", 1280)):
        for f, _, k, l, th, ww, *part in BOARDS:
            if (k, l, th, ww) == cand and part != [2]:
                return f
    return "#"


def links_for(kind, lang, theme, w):
    other = "he" if lang == "en" else "en"
    m = {"./": find("home", lang, theme, w), "benchmarks.html": find("bench", lang, theme, w), "htext.html": find("htext", lang, theme, w),
         "rights.html": find("rights", lang, theme, w)}
    target = find(kind, other, theme, w)
    for href in ("he/benchmarks.html", "../benchmarks.html", "he/", "../", "he/htext.html", "../htext.html", "he/rights.html", "../rights.html"):
        m[href] = target
    return m


DOC_BOARDS = {"spec": B.board_chart_spec, "logo": BR.board_logo, "palette": BR.board_palette, "language": BR.board_language}
OUT_C = HERE.parent / "canvas" / "project"
OUT_T = HERE / "twins"
OUT_H = HERE / "handoff_b"
HEIGHTS = json.loads((HERE / "siteb_heights.json").read_text()) if (HERE / "siteb_heights.json").exists() else {}

MARK_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="HeOCR">'
            '<rect x="7" y="7" width="34" height="34" fill="none" stroke="#2447f9" stroke-width="2"/>'
            + "".join(f'<rect x="{x}" y="{y}" width="6" height="6" fill="#2447f9"/>' for x, y in ((4, 4), (38, 4), (4, 38), (38, 38)))
            + '<path d="M16 18H32V32.5M16 24.5V32.5" fill="none" stroke="{ink}" stroke-width="4.5"/></svg>')


def build():
    BR.DEFAULT = LOGO
    BR.NAMES[LOGO] = BR.NAMES[LOGO].split(" ·")[0] + " · chosen"
    for d in (OUT_H, OUT_H / "he", OUT_T, OUT_C):
        d.mkdir(parents=True, exist_ok=True)
    print("contrast:", B.check_contrast() or "all pass")
    # ---- static handoff
    fav = '<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">\n'
    for page, lang, path, pre in (("bench", "en", "benchmarks.html", ""), ("bench", "he", "he/benchmarks.html", "../"),
                                  ("home", "en", "index.html", ""), ("home", "he", "he/index.html", "../"),
                                  ("htext", "en", "htext.html", ""), ("htext", "he", "he/htext.html", "../"),
                                  ("rights", "en", "rights.html", ""), ("rights", "he", "he/rights.html", "../")):
        html = B.static_page(lang, B.TITLES[(page, lang)], page_body(page, lang, B.STATIC_TOGGLE), pre + "site.css", extra_head=fav.format(p=pre))
        (OUT_H / path).write_text(html, encoding="utf-8")
    (OUT_H / "site.css").write_text(B.CSS, encoding="utf-8")
    for f in ("theme.js", "hero_chart.py"):
        shutil.copy(HERE / "handoff" / f, OUT_H / f)
    (OUT_H / "favicon.svg").write_text(MARK_SVG.format(ink="#0c1222"), encoding="utf-8")
    (OUT_H / "logo-mark.svg").write_text(MARK_SVG.format(ink="#0c1222"), encoding="utf-8")
    (OUT_H / "logo-mark-night.svg").write_text(MARK_SVG.format(ink="#ecebe8").replace("#2447f9", "#8fa3ff"), encoding="utf-8")
    # ---- artboards + twins
    index = {}
    for f, title, kind, lang, theme, w, *part in BOARDS:
        part = part[0] if part else 0
        h = HEIGHTS.get(f, 4000) + 16
        if kind in DOC_BOARDS:
            body, extra, links = DOC_BOARDS[kind](), BR.EXTRA_CSS, {}
            root = f' style="width: {w}px; min-height: {h}px"'
        else:
            body, extra, links = page_body(kind, lang, B.DC_TOGGLE, part), "", links_for(kind, lang, theme, w)
            root = f' style="min-height: {h}px"'
        (OUT_C / f).write_text(B.dc_page(lang, title, body, theme, w, h, links, root, extra), encoding="utf-8")
        twin = body.replace(B.DC_TOGGLE, B.STATIC_TOGGLE)
        html = B.static_page(lang, title, twin, "", inline_css=B.CSS + extra, extra_head='<link rel="stylesheet" href="dfonts.css">\n')
        (OUT_T / f.replace(".dc.html", ".html")).write_text(html.replace('<html ', f'<html data-theme="{theme}" ', 1), encoding="utf-8")
        index[f] = {"title": title, "w": w, "h": h, "kind": kind, "lang": lang, "theme": theme}
    (HERE / "siteb_boards.json").write_text(json.dumps(index, indent=1, ensure_ascii=False))
    print("built", len(index))


if __name__ == "__main__":
    build()
