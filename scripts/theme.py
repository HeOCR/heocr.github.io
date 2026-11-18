"""The site's theme: white by default, a night-mode toggle that applies the dark palette.

One source for every page. The hand-written pages (index, rights, EN and HE) carry these snippets as
apply_theme.py writes them; the generated pages (benchmarks, htext) get them from their build scripts,
and their styles from rights.html, as before.

- The dark palette is the site's ``:root[data-theme="dark"]`` block, unchanged. There is no automatic
  switch on the OS preference: the default is white.
- The choice is kept in localStorage under ``heocr-theme``. Every read and write is wrapped in
  try/catch, so a page renders (white) where storage is blocked.
- The head script runs before the first paint, so a dark choice never flashes white first.
"""

STORAGE_KEY = "heocr-theme"
MARK = "<!-- theme: scripts/theme.py -->"

HEAD = (
    f"{MARK}\n<script>try{{if(localStorage.getItem(\"{STORAGE_KEY}\")===\"dark\")"
    "document.documentElement.setAttribute(\"data-theme\",\"dark\")}catch(e){}</script>\n"
)

CSS = """
  .langbar { gap: 10px; align-items: center; flex-wrap: wrap; }
  .theme-toggle { font: inherit; font-size: 0.95rem; font-weight: 600; padding: 7px 16px; line-height: 1.3; border: 1px solid var(--line); border-radius: 999px; background: var(--surface); color: var(--muted); cursor: pointer; }
  .theme-toggle:hover { background: var(--accent-soft); color: var(--text); }
"""

LABELS = {"en": ("Night mode", "Day mode"), "he": ("מצב לילה", "מצב יום")}


def button(lang: str) -> str:
    night, day = LABELS[lang]
    return (f'<button class="theme-toggle" type="button" aria-pressed="false" data-night="{night}" '
            f'data-day="{day}">{night}</button>')


BODY = (
    "<script>(function(){var b=document.querySelector(\".theme-toggle\");if(!b)return;"
    "var r=document.documentElement;function show(){var d=r.getAttribute(\"data-theme\")===\"dark\";"
    "b.setAttribute(\"aria-pressed\",d?\"true\":\"false\");b.textContent=d?b.getAttribute(\"data-day\"):b.getAttribute(\"data-night\")}"
    "show();b.addEventListener(\"click\",function(){var d=r.getAttribute(\"data-theme\")!==\"dark\";"
    "if(d)r.setAttribute(\"data-theme\",\"dark\");else r.removeAttribute(\"data-theme\");"
    f"try{{localStorage.setItem(\"{STORAGE_KEY}\",d?\"dark\":\"light\")}}catch(e){{}}show()}})}})();</script>\n"
)
