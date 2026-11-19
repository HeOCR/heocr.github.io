"""HeOCR asset pack, direction round: org avatar, master banner (light and dark, Hebrew and English),
and the social preview for the heocr repository. Writes SVGs and a job list for raster.js."""
import json
from pathlib import Path

from hbrand import THEMES, box, grid, lockup, mark, n, svg, text

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TAGLINE = {"en": "Hebrew text out of any document", "he": "טקסט עברי מכל מסמך"}
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
        xx = x + (w - ww if rtl else 0)
        out += f'<rect x="{n(xx)}" y="{n(y + i * pitch)}" width="{n(ww)}" height="{hgt}" fill="{t["muted"] if i < 4 else t["line"]}"/>'
    return out


def wrap(s, face, size, max_w):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text(trial, face, size, 0, 0)[1] > max_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


# ---------------------------------------------------------------- avatar
def avatar(ground, accent, ink):
    size, m = 1024, 600      # the handles reach 363 px from the centre; a circular crop has a 512 px radius
    body = f'<rect width="{size}" height="{size}" fill="{ground}"/>' + mark((size - m) / 2, (size - m) / 2, m, accent, ink, o=2.75, h=7, l=5)
    return svg(size, size, body, "HeOCR")


# ---------------------------------------------------------------- banner
def banner(lang, theme, tag=None):
    t = THEMES[theme]
    W, H, M = 1280, 320, 72
    rtl = lang == "he"
    body = grid(W, H, 32, t) + f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{t["line"]}"/>'
    lk, _ = lockup(W - M if rtl else M, 64, 60, t, "end" if rtl else "start")
    face, size = ("NotoSansHebrew-700", 44) if rtl else ("JetBrainsMono-700", 38)
    pad = 18
    tx = W - M - pad if rtl else M + pad
    tg, tw = text(TAGLINE[lang], face, size, tx, 226, "end" if rtl else "start", t["text"], tracking=0 if rtl else -0.03)
    bx = tx - tw - pad if rtl else M
    by, bh = 226 - size * 0.95 - 6, size * 1.3 + 14
    body += lk + tg + box(bx, by, tw + 2 * pad, bh, t, 2, 10)
    if tag:
        lab, lw = text(tag, "JetBrainsMono-500", 15, 0, 0, fill=t["on"])
        lx = bx + tw + 2 * pad - lw - 16 - 14 if rtl else bx + 14
        body += f'<rect x="{n(lx)}" y="{n(by - 26)}" width="{n(lw + 16)}" height="26" fill="{t["accent"]}"/>' + text(tag, "JetBrainsMono-500", 15, lx + 8, by - 8, fill=t["on"])[0]
    body += skeleton(M if rtl else W - M - 300, 78, 300, t, rtl)
    return svg(W, H, body, f"HeOCR: {TAGLINE[lang]}" + (f" ({tag})" if tag else ""))


# ---------------------------------------------------------------- social preview
def social(lang, repo, desc, theme="light", W=1280, H=640):
    t = THEMES[theme]
    rtl = lang == "he"
    M = 96                                     # safe margin: GitHub and link previews may crop the edges
    end = lambda: W - M if rtl else M
    anchor = "end" if rtl else "start"
    body = grid(W, H, 40, t)
    body += lockup(end(), M, 56, t, anchor)[0]
    pad = 22
    name, nw = text(repo, "JetBrainsMono-700", 84, (W - M - pad) if rtl else (M + pad), 338, anchor, t["text"], tracking=-0.03)
    bx = (W - M - nw - 2 * pad) if rtl else M
    body += name + box(bx, 240, nw + 2 * pad, 128, t, 2.5, 12)
    face = "NotoSansHebrew-400"
    for i, ln in enumerate(wrap(desc, face, 32, 780)[:2]):
        body += text(ln, face, 32, end(), 436 + i * 46, anchor, t["text"], fallback="NotoSansHebrew-400")[0]
    body += text(f"github.com/HeOCR/{repo}", "JetBrainsMono-500", 22, M, H - M + 4, "start", t["muted"])[0]
    body += text("heocr.org", "JetBrainsMono-500", 22, W - M, H - M + 4, "end", t["muted"])[0]
    body += skeleton(M if rtl else W - M - 250, M + 6, 250, t, rtl, rows=4, pitch=20, hgt=8)
    return svg(W, H, body, f"HeOCR/{repo}: {desc}")


if __name__ == "__main__":
    for name, g, a, i in (("avatar", "#ffffff", "#2447f9", "#0c1222"), ("avatar-blue", "#2447f9", "#ffffff", "#ffffff")):
        write(OUT / f"identity/{name}.svg", avatar(g, a, i), OUT / f"identity/{name}-1024.png")
    for lang in ("he", "en"):
        for theme in ("light", "dark"):
            write(OUT / f"banners/banner-{lang}-{theme}.svg", banner(lang, theme), OUT / f"banners/banner-{lang}-{theme}.png", scale=2)
    write(OUT / "banners/example-heocr-en-light.svg", banner("en", "light", "heocr"), OUT / "banners/example-heocr-en-light.png", scale=2)
    D = {"en": "The pipeline and Python package: Hebrew text out of PDFs, Word files, scans and photos.",
         "he": "צינור העיבוד וחבילת הפייתון: טקסט עברי מקובצי PDF, קובצי וורד, סריקות וצילומים."}
    for lang in ("en", "he"):
        write(OUT / f"social/heocr-{lang}.svg", social(lang, "heocr", D[lang]), OUT / f"social/heocr-{lang}-1280x640.png")
    (HERE / "raster_jobs.json").write_text(json.dumps(jobs))
    print(len(jobs), "files")
