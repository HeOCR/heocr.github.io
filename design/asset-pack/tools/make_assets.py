"""HeOCR public asset pack: every image in design/asset-pack/, drawn from repos.json and the brand tokens.

    python make_assets.py                 # everything
    python make_assets.py banner my-repo  # banners for one more repository (he/en, light/dark)
    python make_assets.py post v0.3.0 "One line about the release" [--he "שורה אחת על הגרסה"]
    node raster.js raster_jobs.json       # then: the PNGs

Text is outlined (hbrand.py), so no SVG needs a font or fetches anything."""
import json
import sys
from pathlib import Path

from hbrand import THEMES, box, grid, lockup, mark, n, svg, text

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
REPOS = json.loads((HERE / "repos.json").read_text(encoding="utf-8"))
TAGLINE = {"en": "Hebrew text out of any document", "he": "טקסט עברי מכל מסמך"}
MONO, MONO5, HEB, HEB4 = "JetBrainsMono-700", "JetBrainsMono-500", "NotoSansHebrew-700", "NotoSansHebrew-400"
jobs = []


def write(path, content, png=None, scale=1, transparent=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if png:
        jobs.append(dict(svg=str(path), out=str(png), scale=scale, transparent=transparent))


def skeleton(x, y, w, t, rtl, rows=7, pitch=26, hgt=10):
    widths = (0.62, 1, 1, 0.78, 1, 1, 0.54, 1, 0.7)
    out = ""
    for i in range(rows):
        ww = w * widths[i % len(widths)]
        out += f'<rect x="{n(x + (w - ww if rtl else 0))}" y="{n(y + i * pitch)}" width="{n(ww)}" height="{hgt}" fill="{t["muted"] if i < 4 else t["line"]}"/>'
    return out


def wrap(s, face, size, max_w):
    lines, cur = [], ""
    for w in s.split(" "):
        trial = (cur + " " + w).strip()
        if text(trial, face, size, 0, 0)[1] > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


def tag(label, x, y, t, size=15, anchor="start"):
    """A small filled monospace tag whose bottom edge sits on y. Returns (svg, width)."""
    face = "NotoSansHebrew-500" if any("\u0590" <= c <= "\u05ff" for c in label) else MONO5
    _, lw = text(label, face, size, 0, 0)
    w, h = lw + size * 1.1, size * 1.75
    x0 = x if anchor == "start" else x - w
    return f'<rect x="{n(x0)}" y="{n(y - h)}" width="{n(w)}" height="{n(h)}" fill="{t["accent"]}"/>' + text(label, face, size, x0 + size * 0.55, y - h * 0.3, fill=t["on"])[0], w


def boxed(s, lang, size, x, y, t, o=2.0, hs=10.0, pad=None, label=None, label_size=15):
    """A title in the detection box. x is the start edge of the box (right edge in Hebrew), y the text baseline."""
    rtl = lang == "he"
    face = HEB if rtl else MONO
    pad = pad or size * 0.45
    tx = x - pad if rtl else x + pad
    g, tw = text(s, face, size, tx, y, "end" if rtl else "start", t["text"], tracking=0 if rtl else -0.03)
    bx = x - tw - 2 * pad if rtl else x
    by, bh = y - size * 1.08, size * 1.5
    out = g + box(bx, by, tw + 2 * pad, bh, t, o, hs)
    if label:
        out += tag(label, bx + tw + 2 * pad - hs if rtl else bx + hs, by - o / 2, t, label_size, "end" if rtl else "start")[0]
    return out, tw + 2 * pad


# ---------------------------------------------------------------- identity
def avatar(size=1024):
    m = size * 600 / 1024     # the handles reach 35% of the width from the centre; a circular crop has a 50% radius
    return svg(size, size, f'<rect width="{size}" height="{size}" fill="#ffffff"/>' + mark((size - m) / 2, (size - m) / 2, m, "#2447f9", "#0c1222", o=2.75, h=7, l=5), "HeOCR")


def mono_mark(colour):
    return svg(512, 512, mark(16, 16, 480, colour, colour), "HeOCR")


# ---------------------------------------------------------------- banners
def banner(lang, theme, repo=None):
    t = THEMES[theme]
    W, H, M = 1280, 320, 72
    rtl = lang == "he"
    body = grid(W, H, 32, t) + f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{t["line"]}"/>'
    body += lockup(W - M if rtl else M, 64, 60, t, "end" if rtl else "start")[0]
    body += boxed(TAGLINE[lang], lang, 44 if rtl else 38, W - M if rtl else M, 226, t, label=repo)[0]
    body += skeleton(M if rtl else W - M - 300, 78, 300, t, rtl)
    return svg(W, H, body, f"HeOCR: {TAGLINE[lang]}" + (f" ({repo})" if repo else ""))


# ---------------------------------------------------------------- social previews, og image, card headers
def card(lang, title, lines, foot_start, foot_end="heocr.org", label=None, theme="light", W=1280, H=640, M=96, title_size=84, chips=()):
    """The shared 2:1 card: lockup, a boxed title, up to two lines of text, optional chips, two footers."""
    t = THEMES[theme]
    rtl = lang == "he"
    end = W - M if rtl else M
    anchor = "end" if rtl else "start"
    body = grid(W, H, 40, t) + lockup(end, M, 56, t, anchor)[0]
    while text(title, MONO, title_size, 0, 0, tracking=-0.03)[1] > W - 2 * M - 80:
        title_size -= 4
    _, tw = text(title, MONO, title_size, 0, 0, tracking=-0.03)
    pad, by, bh = 22, 338 - title_size * 1.08, title_size * 1.5
    bx = W - M - tw - 2 * pad if rtl else M
    body += text(title, MONO, title_size, bx + pad, 338, fill=t["text"], tracking=-0.03)[0] + box(bx, by, tw + 2 * pad, bh, t, 2.5, 12)
    if label:
        body += tag(label, bx + tw + 2 * pad - 12 if rtl else bx + 12, by - 1.25, t, 17, anchor)[0]
    y = 436
    for ln in [l for s in lines for l in wrap(s, HEB4, 32, 800)][:2]:
        body += text(ln, HEB4, 32, end, y, anchor, t["text"], fallback=HEB4)[0]
        y += 46
    cx = end
    for c in chips:
        _, cw = text(c, MONO5, 19, 0, 0)
        w = cw + 24
        x0 = cx - w if rtl else cx
        body += f'<rect x="{n(x0)}" y="{n(y - 4)}" width="{n(w)}" height="34" fill="{t["tag"]}"/>' + text(c, MONO5, 19, x0 + 12, y + 19, fill=t["muted"])[0]
        cx += -(w + 10) if rtl else (w + 10)
    body += text(foot_start, MONO5, 22, M, H - M + 4, "start", t["muted"])[0] + text(foot_end, MONO5, 22, W - M, H - M + 4, "end", t["muted"])[0]
    body += skeleton(M if rtl else W - M - 250, M + 6, 250, t, rtl, rows=4, pitch=20, hgt=8)
    return svg(W, H, body, f"HeOCR · {title}: {' '.join(lines)}")


def og_image(lang):
    t = THEMES["light"]
    W, H, M = 1200, 630, 78
    rtl = lang == "he"
    body = grid(W, H, 30, t) + lockup(M, 64, 56, t)[0] + text("heocr.org", MONO5, 24, W - M, 100, "end", t["muted"])[0]
    if rtl:
        g, tw = text(TAGLINE["he"], HEB, 96, W - M - 34, 318, "end", t["text"])
        body += g + box(M, 188, W - 2 * M, 190, t, 3, 14) + tag("h1", M + 14, 188 - 1.5, t, 19)[0]
        for i, ln in enumerate(wrap("נתונים, כלים ומודלים פתוחים לקריאת מסמכים בעברית, מודפסים וכתובים ביד.", HEB4, 34, 900)[:2]):
            body += text(ln, HEB4, 34, W - M, 452 + i * 48, "end", t["text"], fallback=HEB4)[0]
        body += text(TAGLINE["en"], MONO5, 24, W - M, 566, "end", t["muted"])[0]
    else:
        for i, ln in enumerate(("Hebrew text out", "of any document")):
            body += text(ln, MONO, 84, M + 22, 270 + i * 88, fill=t["text"], tracking=-0.03)[0]
        body += box(M, 184, W - 2 * M, 200, t, 3, 14) + tag("h1", M + 14, 184 - 1.5, t, 19)[0]
        for i, ln in enumerate(wrap("Open data, tools and models for reading Hebrew documents, both printed and handwritten.", HEB4, 34, 940)[:2]):
            body += text(ln, HEB4, 34, M, 452 + i * 46, fill=t["text"], fallback=HEB4)[0]
        body += text("זיהוי טקסט עברי, פתוח לכולם", HEB, 26, M, 548, fill=t["muted"])[0]
    return svg(W, H, body, f"HeOCR: {TAGLINE[lang]}")


# ---------------------------------------------------------------- badges
def badge(label, lang="en"):
    """20 px high, the height of a shields.io flat-square badge; square corners, a hairline and one accent handle."""
    t = THEMES["light"]
    rtl = lang == "he"
    face = "NotoSansHebrew-500" if rtl else MONO5
    _, lw = text(label, face, 11, 0, 0, fallback="NotoSansHebrew-500")
    w = round(lw + 28)
    hx = w - 12 if rtl else 6
    g = text(label, face, 11, 8 if rtl else 20, 14, fill=t["text"], fallback="NotoSansHebrew-500")[0]
    return svg(w, 20, f'<rect x="0.5" y="0.5" width="{w - 1}" height="19" fill="{t["bg"]}" stroke="{t["strong"]}"/><rect x="{hx}" y="7" width="6" height="6" fill="{t["accent"]}"/>{g}', f"HeOCR: {label}")


# ---------------------------------------------------------------- the title slide
def slide(lang):
    t = THEMES["light"]
    W, H, M = 1920, 1080, 140
    rtl = lang == "he"
    body = grid(W, H, 40, t) + lockup(W - M if rtl else M, M, 110, t, "end" if rtl else "start")[0]
    body += boxed(TAGLINE[lang], lang, 120 if rtl else 84, W - M if rtl else M, 620, t, 4, 20)[0]
    body += text("heocr.org", MONO5, 34, M, H - M + 10, "start", t["muted"])[0] + text("github.com/HeOCR", MONO5, 34, W - M, H - M + 10, "end", t["muted"])[0]
    return svg(W, H, body, f"HeOCR: {TAGLINE[lang]}")


# ---------------------------------------------------------------- post cards
def post(lang, version, line, shape):
    W, H = {"square": (1080, 1080), "wide": (1600, 900), "slide": (1920, 1080)}[shape]
    t = THEMES["light"]
    rtl = lang == "he"
    M = 96 if shape == "square" else 120
    end, anchor = (W - M if rtl else M), ("end" if rtl else "start")
    body = grid(W, H, 40, t) + lockup(end, M, 72 if shape != "square" else 64, t, anchor)[0]
    cy = H * 0.50
    size = 150 if shape != "square" else 128
    while text(version, MONO, size, 0, 0, tracking=-0.03)[1] > W - 2 * M - 80:
        size -= 6
    _, vw = text(version, MONO, size, 0, 0, tracking=-0.03)
    pad = size * 0.3
    bx = W - M - vw - 2 * pad if rtl else M
    body += text(version, MONO, size, bx + pad, cy + size * 0.36, fill=t["text"], tracking=-0.03)[0] + box(bx, cy - size * 0.62, vw + 2 * pad, size * 1.34, t, 3, 16)
    if shape != "slide":
        body += tag("גרסה חדשה" if rtl else "release", bx + vw + 2 * pad - 16 if rtl else bx + 16, cy - size * 0.62 - 1.5, t, 22, anchor)[0]
    fs = 44 if shape != "square" else 40
    y = cy + size * 0.72 + fs * 1.6
    for ln in wrap(line, HEB4, fs, W - 2 * M - (0 if shape == "square" else 300))[:3]:
        body += text(ln, HEB4, fs, end, y, anchor, t["text"], fallback=HEB4)[0]
        y += fs * 1.4
    body += text("heocr.org", MONO5, 26, M, H - M + 6, "start", t["muted"])[0] + text("github.com/HeOCR", MONO5, 26, W - M, H - M + 6, "end", t["muted"])[0]
    return svg(W, H, body, f"HeOCR {version}: {line}")


def banners_for(repo):
    for lang in ("he", "en"):
        for theme in ("light", "dark"):
            name = f"{repo}-{lang}-{theme}" if repo else f"banner-{lang}-{theme}"
            d = OUT / "banners" / (repo or "master")
            write(d / f"{name}.svg", banner(lang, theme, repo), d / f"{name}.png", scale=2)


def everything():
    write(OUT / "identity/avatar.svg", avatar(), OUT / "identity/avatar-1024.png")
    for name, colour in (("mark-mono-black", "#000000"), ("mark-mono-white", "#ffffff")):
        write(OUT / f"identity/{name}.svg", mono_mark(colour), OUT / f"identity/{name}-512.png", transparent=True)
    banners_for(None)
    for repo, r in REPOS["repos"].items():
        banners_for(repo)
        for lang in ("en", "he"):
            write(OUT / f"social/{repo}-{lang}.svg", card(lang, repo, [r[lang]], f"github.com/HeOCR/{repo}"), OUT / f"social/{repo}-{lang}-1280x640.png")
    for lang in ("he", "en"):
        write(OUT / f"og/og-image-{lang}.svg", og_image(lang), OUT / f"og/og-image-{lang}-1200x630.png")
    for key, b in REPOS["badges"].items():
        for lang in ("en", "he"):
            write(OUT / f"badges/{key}-{lang}.svg", badge(b[lang], lang))
    for m in REPOS["models"]:
        for lang in ("en", "he"):
            write(OUT / f"cards/model-{m['name']}-{lang}.svg",
                  card(lang, m["name"], [REPOS["model_line"][lang]], "huggingface.co/HeOCR", label="model", chips=(m["licence"], "Tesseract", "Hebrew")),
                  OUT / f"cards/model-{m['name']}-{lang}-1280x640.png")
    for d in REPOS["datasets"]:
        for lang in ("en", "he"):
            write(OUT / f"cards/dataset-{d['name']}-{lang}.svg",
                  card(lang, d["name"], [d[lang]], "github.com/HeOCR/htext", label="dataset", chips=(d["licence"], "Hebrew")),
                  OUT / f"cards/dataset-{d['name']}-{lang}-1280x640.png")
    ex = REPOS["post_example"]
    for lang in ("en", "he"):
        for shape in ("square", "wide"):
            W = {"square": "1080x1080", "wide": "1600x900"}[shape]
            write(OUT / f"posts/example-release-{shape}-{lang}.svg", post(lang, ex["version"], ex[lang], shape), OUT / f"posts/example-release-{shape}-{lang}-{W}.png")
        write(OUT / f"posts/title-slide-{lang}.svg", slide(lang), OUT / f"posts/title-slide-{lang}-1920x1080.png")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["banner"]:
        banners_for(a[1])
    elif a[:1] == ["post"]:
        he = a[a.index("--he") + 1] if "--he" in a else None
        for shape in ("square", "wide"):
            write(OUT / f"posts/{a[1]}-{shape}-en.svg", post("en", a[1], a[2], shape), OUT / f"posts/{a[1]}-{shape}-en.png")
            if he:
                write(OUT / f"posts/{a[1]}-{shape}-he.svg", post("he", a[1], he, shape), OUT / f"posts/{a[1]}-{shape}-he.png")
    else:
        everything()
    (HERE / "raster_jobs.json").write_text(json.dumps(jobs))
    print(len(jobs), "PNG jobs")
