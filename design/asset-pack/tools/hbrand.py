"""HeOCR asset pack: shared drawing helpers. Text is outlined to paths with fontTools, so the SVGs render
without any font installed and fetch nothing. Hebrew is laid out right to left with a small bidi pass
(Latin and digit runs stay left to right), which is enough for unpointed text."""
import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
THEMES = {
    "light": dict(bg="#ffffff", text="#0c1222", muted="#56607a", line="#dfe3f2", strong="#b9c1de", accent="#2447f9", tag="#eef0f7", grid="#f1f3fb", on="#ffffff"),
    "dark": dict(bg="#141414", text="#ecebe8", muted="#a29d94", line="#2e2d2b", strong="#4a4844", accent="#8fa3ff", tag="#262523", grid="#1a1a1a", on="#0b1020"),
}
_cache = {}


def font(name):
    if name not in _cache:
        f = TTFont(FONTS / f"{name}.ttf")
        _cache[name] = (f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _cache[name]


def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s or "0"


def visual(text):
    """Logical to visual order for a line whose base direction is right to left."""
    if not re.search(r"[֐-׿]", text):
        return text
    runs = re.findall(r"[A-Za-z0-9][A-Za-z0-9.\-+/]*|[^A-Za-z0-9]+", text)
    out = []
    for r in reversed(runs):
        if re.match(r"[A-Za-z0-9]", r):
            out.append(r)
        else:
            out.append(r[::-1].translate(str.maketrans("()[]", ")(][")))
    return "".join(out)


def text(s, face, size, x, y, anchor="start", fill="#000", fallback="NotoSansHebrew-700", tracking=0.0):
    """Returns (svg path element, width). anchor: start (x is the left edge), end (x is the right edge), middle."""
    f, gs, cmap, upm = font(face)
    f2, gs2, cmap2, upm2 = font(fallback)
    k = size / upm
    pen_x, parts = 0.0, []
    for ch in visual(s):
        cp = ord(ch)
        g, gset, scale, src = (cmap[cp], gs, k, f) if cp in cmap else (cmap2.get(cp, ".notdef"), gs2, size / upm2, f2)
        parts.append((g, gset, scale, pen_x))
        pen_x += src["hmtx"][g][0] * scale + tracking * size
    width = pen_x - tracking * size
    x0 = x if anchor == "start" else x - width if anchor == "end" else x - width / 2
    d = []
    for g, gset, scale, px in parts:
        pen = SVGPathPen(gset, ntos=n)
        gset[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x0 + px, y)))
        c = pen.getCommands()
        if c:
            d.append(c)
    return f'<path fill="{fill}" d="{" ".join(d)}"/>', width


def mark(x, y, size, accent, ink, o=2.0, h=6.0, l=4.5):
    """Logo 1 on its 48-unit grid, as filled shapes. o, h, l: outline, handle and letter weights."""
    s = size / 48
    X = lambda v: n(x + s * v)
    Y = lambda v: n(y + s * v)
    a, b, c, e = 7 - o / 2, 41 + o / 2, 7 + o / 2, 41 - o / 2
    box = f"M{X(a)},{Y(a)}H{X(b)}V{Y(b)}H{X(a)}Z M{X(c)},{Y(c)}V{Y(e)}H{X(e)}V{Y(c)}Z"
    for cx, cy in ((7, 7), (41, 7), (7, 41), (41, 41)):
        box += f" M{X(cx - h / 2)},{Y(cy - h / 2)}H{X(cx + h / 2)}V{Y(cy + h / 2)}H{X(cx - h / 2)}Z"
    letter = (f"M{X(16)},{Y(18 - l / 2)}H{X(32 + l / 2)}V{Y(32.5)}H{X(32 - l / 2)}V{Y(18 + l / 2)}H{X(16)}Z "
              f"M{X(16 - l / 2)},{Y(24.5)}H{X(16 + l / 2)}V{Y(32.5)}H{X(16 - l / 2)}Z")
    return f'<path fill="{accent}" d="{box}"/><path fill="{ink}" d="{letter}"/>'


def lockup(x, y, mark_size, t, anchor="start"):
    """Mark plus the HeOCR wordmark, always left to right. y is the top of the mark. Returns (svg, width)."""
    size = mark_size * 0.62
    gap = mark_size * 0.26
    he, w1 = text("He", "JetBrainsMono-700", size, 0, 0, fill=t["text"], tracking=-0.03)
    ocr, w2 = text("OCR", "JetBrainsMono-700", size, 0, 0, fill=t["accent"], tracking=-0.03)
    total = mark_size + gap + w1 + w2 - 0.03 * size
    x0 = x if anchor == "start" else x - total
    base = y + mark_size * 0.5 + size * 0.36
    he, _ = text("He", "JetBrainsMono-700", size, x0 + mark_size + gap, base, fill=t["text"], tracking=-0.03)
    ocr, _ = text("OCR", "JetBrainsMono-700", size, x0 + mark_size + gap + w1, base, fill=t["accent"], tracking=-0.03)
    return mark(x0, y, mark_size, t["accent"], t["text"]) + he + ocr, total


def grid(w, h, step, t, sw=1.0):
    d = "".join(f"M{x},0V{h}" for x in range(step, w, step)) + "".join(f"M0,{y}H{w}" for y in range(step, h, step))
    return f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/><path d="{d}" stroke="{t["grid"]}" stroke-width="{n(sw)}" fill="none"/>'


def box(x, y, w, h, t, o=1.5, hs=8.0):
    """The detection box: outline plus four square handles centred on its corners."""
    r = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="none" stroke="{t["accent"]}" stroke-width="{n(o)}"/>'
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        r += f'<rect x="{n(cx - hs / 2)}" y="{n(cy - hs / 2)}" width="{n(hs)}" height="{n(hs)}" fill="{t["accent"]}"/>'
    return r


def svg(w, h, body, title, desc=""):
    d = f"<desc>{desc}</desc>" if desc else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">'
            f"<title>{title}</title>{d}{body}</svg>\n")
