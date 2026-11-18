# HeOCR site: files and markup

Static and framework-free. The HTML files are reference output: open them in a browser, then copy the markup patterns into the generator scripts.

| File | What it is |
|---|---|
| `site.css` | The whole system: tokens for light and night, header, footer, tables, chart styling, badges, empty states, the box, home and document-page pieces. One file for every page, EN and HE. |
| `theme.js` | Theme toggle. Light by default whatever the OS setting; night mode only through the toggle, remembered in `localStorage` under `heocr-theme`. |
| `hero_chart.py` | Hero chart generator, standard library only. `hero_svg(results["documents"], lang, variant)` returns one inline `<svg>`. |
| `favicon.svg`, `logo-mark.svg`, `logo-mark-night.svg` | The mark as standalone files (48-unit grid). |
| `benchmarks.html`, `he/benchmarks.html` | Benchmarks page, built from `results.json` (file dated 2026-11-17). |
| `index.html`, `he/index.html` | Home page. |
| `htext.html`, `he/htext.html` | htext page, from the files dated 2026-11-18 (three corpora). |
| `rights.html`, `he/rights.html` | Rights and takedown page. |

## Brand in one paragraph

The site speaks the language of OCR output. A blue box with four square handles marks a detected region, and a small monospace tag names it. Everything else is quiet: white ground, square corners (2 px), 1 px hairlines, no shadows. Blue `#2447f9` is the brand and the interface; green and red appear only in the chart (heocr, best other tool) and the verdict badges. Headings, labels and figures are JetBrains Mono; body text and all Hebrew are Noto Sans Hebrew.

## Wiring a page

```html
<html lang="en" dir="ltr">            <!-- he: lang="he" dir="rtl"; nothing else changes -->
<head>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+Hebrew:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="site.css">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <script>(function(){try{if(localStorage.getItem("heocr-theme")==="dark")document.documentElement.dataset.theme="dark"}catch(e){}})()</script>
</head>
<body class="site">                   <!-- .site is required: it is the container the breakpoints query -->
  ...
  <script src="theme.js"></script>
</body>
```

- Remove today's `@media (prefers-color-scheme: dark)` block. Night mode is `[data-theme="dark"]` only.
- The language switch stays two plain links (`.lang-toggle`), no script.
- Breakpoints are container queries on `.site` (820 px and 640 px), not media queries.

## Logo

The logo is inline SVG so it follows the theme. Copy the `<a class="brand">` block from any HTML file:

```html
<a class="brand" href="./" aria-label="HeOCR">
  <svg viewBox="0 0 48 48" aria-hidden="true">…box, four handles, the letter ה…</svg>
  <span dir="ltr">He<b>OCR</b></span>
</a>
```

`He` takes the text colour, `OCR` the accent. Keep `dir="ltr"` on the wordmark so it reads the same on Hebrew pages.

## The box

| Use | Markup |
|---|---|
| Page title | `<h1><span class="bb" data-tag="h1 · 0.99">HeOCR benchmarks</span></h1>` |
| Hero figure | `<div class="panel" data-tag="figure · hero">` inside `<figure class="hero-chart">` |
| Grid behind the page head | `<div class="band gridband"><div class="wrap page-head">…</div></div>` |
| "Ours" row | `tr.ours` (two blue rules and a filled `ours` tag; nothing to add) |

Rules: only the logo, the page title, the hero figure and the "ours" rows get a box. The tag is optional and sits on the start side, so it moves to the right on Hebrew pages by itself. Under 640 px the hero figure drops its box and keeps a blue top rule, so the chart can use the full width.

## Hero chart

```python
from hero_chart import hero_svg, finding_sentence, legend_marker
doc = results["documents"]
svg = hero_svg(doc, lang, "wide") + hero_svg(doc, lang, "narrow")   # emit both
headline = finding_sentence(doc, lang)                               # computed, never hand-written
```

`site.css` shows the wide SVG above an 820 px container and the narrow one below it. What the generator guarantees:

- every entry of `documents.cells` is drawn, in file order;
- one linear axis from 0 to 100%, never truncated;
- per type: heocr (green circle), the lowest-error reader among Docling, MarkItDown and PyMuPDF4LLM (red hollow square), and stock Tesseract wherever it has a `cer` (grey diamond);
- a missing score is a text line in the lane, never a mark on the axis;
- intervals are drawn to scale and also printed as numbers;
- Hebrew output is mirrored (zero on the right) while numbers stay left-to-right.

Green and red are the pair colour-blind readers most often confuse, which is why shape, row position and the name label always repeat the identity. Geometry constants are the `GEOM` dict; short chart labels per type are in `TYPE_LABELS` (a new document type needs an entry in both languages).

## Markup that changed from today's pages

Class names you already emit still work: `.wrap`, `.lede`, `.sub`, `.note`, `.btn`, `.card`, `.grid`, `.meta`, `.flow`, `.status`, `.empty`, `.tablewrap`, `.ci`, `tr.ours`, `.facts`, `.lang-toggle`, `.stats`, `.stat`, `.credit`.

| Change | New markup |
|---|---|
| Header and footer | `<header class="site-header">` and `<footer class="site-footer">`; see any HTML file. The `← HeOCR` back link is gone; the logo links home. |
| Page head | The old `<header>` content moves into `.band.gridband > .wrap.page-head`, with the boxed `h1`. |
| Page index | `<nav class="wrap"><div class="toc"><a href="#p-mod">Name<small>Status</small></a>…</div></nav>`: one link per section, no separator characters. `<small>` is optional (htext has none). |
| Section head (Benchmarks) | `<div class="domain-head"><h2>…</h2><span class="status">No data yet</span></div>`; add class `scored` for a scored domain. |
| Tables are grouped | One `<table>` per domain with one `<tbody>` per slice or document type, each starting with `<tr class="group"><th colspan="N" scope="rowgroup" id="doc-pdf-t1"><span class="gtitle">Title <span class="note">· PDF T1 · 318 documents</span></span></th></tr>`. Historical print: 5 tables become 1. Documents: 10 become 2. |
| Format-specific measure | "Section numbers correct" (DOCX) and "Words in image regions found" (PDF T6) share the last column; the column head is in that type's group row, `<th class="colh" scope="col">`. |
| Value and interval | `<td class="num"><span class="v"><bdi dir="ltr">0.27%</bdi></span><span class="ci"><bdi dir="ltr">0.19–0.35%</bdi></span></td>`. Not measured: `<td class="num na">–</td>`. Not applicable: `<td class="nap"></td>`. |
| Direction | `<span class="dir">lower is better</span>` or `<span class="dir up">higher is better</span>`; the arrow comes from CSS. |
| Ours | `tr.ours` plus `<span class="tag-ours">ours</span>` after the name. |
| Sample size that differs | `<span class="tag-n block">n = 80</span>` after the reader name. |
| Method lists | `ul.facts` wrapped in `<details class="method"><summary>…</summary>…</details>`, closed by default; add `open` to show them. |
| Small-set warning | `<p class="warn"><svg class="ico">…</svg><span>…</span></p>`. |
| Verdict badge | `<span class="verdict supported|unsupported|pending"><svg class="ico">…</svg>Label</span>`; add `lg` for the large size. |
| Gate summary | `.gate-summary` (strip of `.gate-cell` plus a count) and `ul.gate-list`; see the Release gate section. |
| Home | `<div class="home-hero band gridband">` with the boxed `h1`; `main` gets class `home`; the Benchmarks button gets `btn primary`. |
| htext | `main` keeps `class="wrap doc ht"`; its inline `<nav class="toc">` moves out into the page index above. |
| Rights | `main` keeps `class="wrap doc"`; the section markup is unchanged. |

## Still to confirm

1. **Verdict field.** `results.json` has `documents.gate: "not_run"` and no verdicts. The design expects each cell to gain one, for example `cells["PDF T1"].verdict = "supported" | "not_supported"`, mapped to the `supported` / `unsupported` classes.
2. **Run date.** `documents` has no date of its own, so the chart caption uses the top-level `updated`.
3. **New wording, both languages.** Chart title, legend and missing-score lines; the computed headline; the axis note in the caption; the two-sentence Release gate introduction; "Awaiting run"; "Method, reference and run"; the note on a dash versus an empty cell. The Hebrew needs a native read. Method, rights and licence wording is copied unchanged.
