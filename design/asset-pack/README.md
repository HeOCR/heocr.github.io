# HeOCR public asset pack: direction round

The first step the brief asks for: the **org avatar**, the **master banner** (light and dark, Hebrew and English) and **one social preview** (for `heocr`), shown before the full set. Prepared 2026-11-19. Nothing here is installed anywhere and nothing here is final.

Look at `direction.png` first.

| Asset | Size | Files | Where it will go |
|---|---|---|---|
| Org avatar, white ground (recommended) | 1024 × 1024 | `identity/avatar.svg`, `identity/avatar-1024.png` | GitHub org, Hugging Face org, Zenodo community (uploaded by hand) |
| Org avatar, blue ground (alternate) | 1024 × 1024 | `identity/avatar-blue.svg`, `identity/avatar-blue-1024.png` | The same; pick one |
| Avatar in a circle at 40, 96, 200 px | | `identity/avatar-circle-test.png` | Check only |
| Master banner | 1280 × 320, PNG at 2× | `banners/banner-{he,en}-{light,dark}.svg` and `.png` | README tops, through `<picture>` |
| Per-repo banner, one example | same | `banners/example-heocr-en-light.*` | Shows the repo tag on the box |
| Social preview for `heocr` | 1280 × 640 | `social/heocr-{he,en}.svg`, `social/heocr-{he,en}-1280x640.png` | Repository Settings → Social preview (by hand) |
| Generator | | `tools/` | `python make_assets.py`, then `node raster.js raster_jobs.json` |

## What this direction proposes

- **Avatar:** the mark alone on a plain ground, in the heavier "icon weight" drawn for the Android launcher, so it holds at 40 px. Its handles stay well inside a circular crop.
- **Banner:** the grid ground of the site's page head, the lockup, and the tagline inside the box. A few plain lines stand for a page on the far side. The dark variant uses the brand's night tokens. Hebrew is mirrored; the lockup stays left to right.
- **Per-repo banner:** the same frame with the repo's name as a small filled tag on the box.
- **Social preview:** the repo name in the box, one sentence, the lockup, and two addresses. Content sits inside a 96 px margin.
- **Text is outlines.** Every SVG holds paths only: no `<text>`, no font reference, nothing fetched. The words are in each file's `<title>`.

## Limits checked so far

| Place | Limit | Source, checked 2026-11-19 |
|---|---|---|
| GitHub social preview | PNG, JPG or GIF under 1 MB; at least 640 × 320, 1280 × 640 for best display | [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview) |
| Hugging Face model card | `thumbnail` is a URL to an image used in social sharing; light and dark images are switched with `#hf-light-mode-only` / `#hf-dark-mode-only` or the `dark:hidden` / `hidden dark:block` classes | [Hub docs: Model Cards](https://huggingface.co/docs/hub/model-cards) |

Not checked yet, and needed before the full set: GitHub avatar limits, Zenodo's community logo, PyPI's image rendering, Hugging Face's org avatar.

## File sizes

Banner PNGs are 28 to 35 KB (limit 300 KB). Social previews are 34 and 44 KB (limit 1 MB). Avatars are 4 KB. PNGs were saved with Pillow's optimiser; oxipng was not available here.

## Sources

| Asset | Source | Licence |
|---|---|---|
| The mark, tokens, the box, the grid | The brand handover (`design/brand-handover/`) | Project's own |
| Icon weight of the mark | The Android design (`design/android/` in `heocr-desktop`) | Project's own |
| JetBrains Mono, Noto Sans Hebrew (outlined into the images; static instances in `tools/fonts/` for the generator) | `google/fonts` | SIL OFL 1.1 |

## Questions for the owner, through the lead

1. **Avatar ground:** white or blue. This is the same choice as the Android launcher icon, and the two should match.
2. **The banner's far side:** the plain page lines, or nothing there at all.
3. **The one-line descriptions** on social previews are new wording; each repo's should come from its maintainer.

## Not verified

Nothing was uploaded to GitHub, PyPI, Hugging Face or Zenodo, so real cropping and rendering there are untested. The `<picture>` snippet comes with the full set.

---

`design[claude/claude-code#shay-macbook-m4]@heocr/opensource`
