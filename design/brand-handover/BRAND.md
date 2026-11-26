# HeOCR brand guide: Bounding Box

## The idea

HeOCR turns pictures of Hebrew text into text. The brand borrows the picture every OCR engineer knows: a detected region, drawn as a box with handles and a small label. On the site, a blue box with four square handles marks a detected region and a monospace tag names it. Everything else stays quiet: a white ground, square corners, hairlines, no shadows.

Tone: credible and scientific, an open-source project that shows its work. Confident, never hype.

## Logo

The mark is the Hebrew letter ה, drawn from three straight strokes on a 48-unit grid, inside a detection box with four handles. ה is also the "He" of HeOCR. The wordmark is `HeOCR` in JetBrains Mono Bold: `He` in the text colour, `OCR` in brand blue.

| File | Use |
|---|---|
| `logo/svg/lockup.svg`, `lockup-night.svg` | Mark plus wordmark, for light and dark grounds. The wordmark is outlined. |
| `logo/svg/mark.svg`, `mark-night.svg` | Mark alone: favicon, avatars, small spaces. |
| `logo/svg/*-mono-black.svg`, `*-mono-white.svg` | Single-colour versions for print, stamps and embossing. |
| `logo/png/` | Raster exports of the same, plus the link-preview image. |

Rules:

- Keep clear space around the logo of at least a quarter of the mark's width.
- Smallest sizes: 16 px for the mark, 20 px high for the lockup.
- On the site the logo is inline SVG, so it follows the theme; see the header in either rights reference page under `site/`.
- Keep the wordmark left-to-right on Hebrew pages. The mark sits on the start side: left in English, right in Hebrew.
- Do not recolour it outside the supplied versions, round its corners, add a shadow, or set the wordmark in another typeface.
- The lowercase `heocr` is the package name, written in code style. It is not a second logo.

## Colour

One brand colour, detection blue, on white. Green and red are reserved for data: heocr and the best other tool in the chart, and the two verdicts. Light is the default whatever the visitor's OS setting; night mode is entered only through the toggle. The six night neutrals are the site's earlier values, unchanged.

| Token | Light | Night | Role |
|---|---|---|---|
| `--bg` | `#ffffff` | `#141414` | Page ground |
| `--surface` | `#f6f7fc` | `#1c1c1c` | Table heads, quiet panels, footer |
| `--text` | `#0c1222` | `#ecebe8` | Text |
| `--muted` | `#56607a` | `#a29d94` | Secondary text, labels |
| `--line` | `#dfe3f2` | `#2e2d2b` | Hairlines inside components |
| `--line-strong` | `#b9c1de` | `#4a4844` | Section rules, control borders |
| `--accent` | `#2447f9` | `#8fa3ff` | Brand blue: links, the box, current page, primary button |
| `--accent-soft` | `#eef1ff` | `#1b2040` | "Ours" row tint, hover |
| `--tag` | `#eef0f7` | `#262523` | Chips, code background |
| `--on-accent` | `#ffffff` | `#0b1020` | Text on the accent |
| `--grid` | `#f1f3fb` | `#1a1a1a` | Grid behind the page head |
| `--series-ours` | `#15803d` | `#1f9d55` | Chart: heocr (green circle) |
| `--series-alt` | `#dc2626` | `#f0564a` | Chart: best other open tool (red hollow square) |
| `--series-tess` | `#64748b` | `#8892a0` | Chart: stock Tesseract (grey diamond) |
| `--ok` | `#166534` | `#7fcf9f` | Verdict: supported |
| `--ok-soft` | `#e7f4ec` | `#18281f` | Supported badge ground |
| `--no` | `#a12a22` | `#ee9a8b` | Verdict: not supported |
| `--no-soft` | `#fbe9e7` | `#31201c` | Not-supported badge ground |

All text pairs meet WCAG AA (4.5:1) in both themes; the measured ratios are on `reference/brand/palette-and-type.png`.

Green and red are the pair colour-blind readers most often confuse. In the chart, identity is therefore always repeated by shape, by row position and by a name label, and the verdict badges always carry an icon and a word.

## Type

| Role | Face | Notes |
|---|---|---|
| Headings, labels, tags, figures, navigation | JetBrains Mono 500 and 700 | Headings use a letter-spacing of -0.035em. |
| Body text, and all Hebrew | Noto Sans Hebrew 400, 500, 700 | JetBrains Mono has no Hebrew letters, so Hebrew headings fall to Noto Sans Hebrew at the same weight. |
| Code | JetBrains Mono | On a `--tag` ground. |

Sizes: h1 from 1.9rem to 2.9rem, h2 1.45rem, h3 1.02rem, lede 1.1rem, body 1rem at 1.6 line height, small 0.9rem, micro 0.76rem. Numbers use tabular figures and stay left-to-right in Hebrew.

## The box

| Part | Specification |
|---|---|
| Outline | 1.5 px, `--accent`, offset 8 px from the content |
| Handles | Four 8 px squares in `--accent`, centred on the corners |
| Tag | Optional. JetBrains Mono 700, 0.68rem, on `--accent`, above the box on the start side. It names the region: `h1`, `figure · hero`. |
| Grid | A 28 px hairline grid in `--grid`, behind the page head only |

What gets a box: the logo, the page title, the hero figure, and the "ours" rows in tables (as two blue rules). Nothing else. Using the box on ordinary content weakens it.

## Shape and layout

- Square corners everywhere: 2 px radius.
- 1 px hairlines in `--line`; 1 px `--line-strong` for section tops, table heads and control borders.
- No shadows and no gradients.
- Content width 1160 px with a 24 px gutter, 16 px on a phone.
- The current page in the navigation is bracketed in blue: `[Benchmarks]`.

## Components

All of these are in `site/site.css`, and documented in `site/MARKUP.md`: header with language switch and theme toggle, footer, page head, page index, grouped table with the "ours" row, value with its 95% interval, direction labels, status chips, no-data card, verdict badge, release-gate summary, method disclosure, cards and buttons.

The chart generator is `site/hero_chart.py`. For current benchmark examples, use the maintained [benchmark page](https://heocr.org/en/benchmarks.html).

## Hebrew and right-to-left

The same design serves both languages. Layout is written with logical properties, so `dir="rtl"` mirrors it with no extra rules: the logo moves to the right, the tag moves to the right-hand corner of its box, and the chart draws its zero line on the right. Numbers, identifiers and the wordmark stay left-to-right.
