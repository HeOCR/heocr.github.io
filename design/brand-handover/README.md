# HeOCR brand and site handover

The "Bounding Box" brand for HeOCR and the redesigned site (home, Benchmarks, htext, rights; English and Hebrew; light and night). Prepared 2026-11-18.

> **This folder is in a transient location.** `~/temp` can be wiped at any time. The first job is to copy this whole folder into a proper GitHub repository, commit it and push it. Do not treat `~/temp` as the home of these files.

## What is in here

| Path | What it is |
|---|---|
| `README.md` | This file. |
| `BRAND.md` | The brand guide: concept, logo rules, colour tokens, type, the box, components, accessibility. |
| `PROMPT.md` | A short prompt to hand to the developer or coding agent who takes this in. |
| `site/` | Drop-in reference build: `site.css`, `theme.js`, `hero_chart.py`, `favicon.svg`, and every page as static HTML (`index`, `benchmarks`, `htext`, `rights`, plus `he/` versions). |
| `site/MARKUP.md` | How to wire a page, and every markup pattern that changed from the current site. Read this before touching the generator scripts. |
| `logo/svg/` | Mark and lockup as SVG: colour, night, mono black, mono white. The lockup wordmark is outlined, so it needs no font. |
| `logo/png/` | Mark at 16 to 512 px, lockup at 1x, 2x and 4x, `apple-touch-icon.png`, a maskable icon, and `og-image-1200x630.png` for link previews. |
| `logo/favicon.svg`, `logo/favicon.ico` | Favicons (the `.ico` holds 16, 32 and 48 px). |
| `tokens/tokens.css` | The colour, type and shape custom properties on their own. |
| `tokens/tokens.json` | The same tokens as data, for light and night. |
| `reference/pages/` | Full-page screenshots of every page: desktop (1280 px) and phone (375 px), light and night, English and Hebrew. Use them to compare against your build. The phone Benchmarks page comes as two images, top and bottom. |
| `reference/brand/` | The brand boards: logo options, palette and type, design language, hero chart specification. |
| `reference-generator/` | The scripts that produced `site/`. Reference only, not production code; see the note inside. |

## How to adopt it

1. **Back it up.** Copy this folder into the site repository (for example `design/brand-handover/`), commit and push.
2. **Read** `BRAND.md` and `site/MARKUP.md`.
3. **Stylesheet and script.** Use `site/site.css` and `site/theme.js` as they are. Remove the per-page inline `<style>` blocks and the old theme script.
4. **Generators.** Change the Python page generators to emit the markup in `site/*.html`. The page wording does not change; only the shell and a few patterns do (header, footer, page head, page index, grouped tables, badges).
5. **Hero chart.** Call `hero_chart.py` from the Benchmarks generator. It reads `results.json` and returns the inline SVG.
6. **Logo and icons.** Copy `logo/favicon.svg`, `logo/favicon.ico` and `logo/png/apple-touch-icon.png` to the site root, and add `og-image-1200x630.png` as the `og:image` if you want link previews.
7. **Compare** each generated page with `reference/pages/`.

## Checks before it ships

- No horizontal page scroll at 375 px on any page; wide tables scroll inside their own box.
- Light is the default whatever the OS setting; night mode only through the toggle, and it survives a reload.
- English and Hebrew pages have the same structure; Hebrew is mirrored by `dir="rtl"` alone.
- Every number on the Benchmarks page comes from `results.json`, with its sample size and 95% interval.
- The hero chart shows every document type, on one axis from 0 to 100%, with only the readers in the file.
- Method, rights and licence wording is unchanged from the current pages.

## Open items

1. **Verdict field.** `results.json` has `documents.gate: "not_run"` and no verdicts, so the Release gate section shows ten "Awaiting run" badges. Once each document type carries a verdict, map it to the `supported` or `unsupported` badge class (details in `site/MARKUP.md`).
2. **Run date.** `documents` has no date field of its own, so the chart caption uses the top-level `updated`.
3. **New wording.** A few strings are new in both languages (chart title, legend, missing-score lines, computed headline, caption note, Release gate introduction). They are listed in `site/MARKUP.md` and can be edited freely.

## What the build was made from

- `benchmarks/results.json` dated 2026-11-17 (run `synth-2026-11-17-main`).
- The home, Benchmarks, htext and rights pages as they stood on 2026-11-18.

## Fonts

JetBrains Mono (headings, labels, figures) and Noto Sans Hebrew (body text and all Hebrew), both from Google Fonts under the SIL Open Font License. The link tag is in `site/MARKUP.md`.

The old home, benchmark and corpus examples now forward to their maintained public pages. Use the live pages for the current release status and registered results.
