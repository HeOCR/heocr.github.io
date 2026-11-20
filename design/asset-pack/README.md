# HeOCR public asset pack

The images and text snippets HeOCR shows wherever it lives: the GitHub organisation and repositories, PyPI, Hugging Face, Zenodo, link previews and release posts. Everything follows the Bounding Box brand. Prepared 2026-11-20; it replaces the direction round and follows the owner's answers on pull request 28 (avatar on white, page lines kept, descriptions from the maintainers).

Look at `overview.png` first. Nothing here is installed anywhere: installing is the lead's job after review, and the steps marked **by hand** need a maintainer with access.

## Index

| Asset | Size | Files | Where it goes | How to install |
|---|---|---|---|---|
| Org avatar | 500 × 500 and 1024 × 1024 PNG, SVG | `identity/avatar-500.png`, `avatar-1024.png`, `avatar.svg` | GitHub org, Hugging Face org, Zenodo community | **By hand.** GitHub: organisation Settings → Profile picture, upload `avatar-500.png`. Hugging Face: organisation settings → avatar, `avatar-1024.png`. Zenodo: community Settings → Profile → logo, `avatar-500.png` |
| Avatar check | | `identity/avatar-circle-test.png` | Check only | The avatar in a circle at 40, 96 and 200 px on light and dark |
| Monochrome mark | 512 × 512 PNG (transparent), SVG | `identity/mark-mono-black.*`, `mark-mono-white.*` | Places that tint or need one colour | As needed |
| Master banner | 1280 × 320, PNG at 2× (2560 × 640), SVG | `banners/master/banner-{he,en}-{light,dark}.*` | Org profile README; any README without a repo tag | Through `<picture>`; see `templates/README-header.md` |
| Per-repo banners | same | `banners/<repo>/<repo>-{he,en}-{light,dark}.*` for the eight repositories | Top of each repository's README (and so PyPI's page for `heocr`) | Paste the snippet from `templates/README-header.md` |
| Social previews | 1280 × 640 PNG, SVG | `social/<repo>-{he,en}-1280x640.png` | Each repository's link preview | **By hand.** Repository Settings → General → Social preview → upload. One image per repository: Hebrew or English, the maintainer's choice |
| og:image, Hebrew | 1200 × 630 PNG, SVG | `og/og-image-he-1200x630.png` | heocr.org site root | The lead adds it to the site and points the Hebrew pages' `og:image` at it |
| og:image, English, refreshed | 1200 × 630 | `og/og-image-en-1200x630.png` | heocr.org `/en/` | Optional; see "Notes for the lead" |
| Badges | 20 px high SVG | `badges/{hebrew-first,offline,open-data-cc0,apache-2}-{en,he}.svg` | README badge rows | `<img>` by absolute URL; see the snippet |
| Model card header | 1280 × 640 PNG, SVG | `cards/model-<name>-{en,he}-1280x640.png` | Hugging Face model card and its `thumbnail`; Zenodo record | See `templates/model-card-header.md`. **By hand** on Zenodo |
| Dataset header | 1280 × 640 | `cards/dataset-htext-{en,he}-1280x640.png` | htext releases on Zenodo and GitHub | Same |
| Release post cards | 1080 × 1080 and 1600 × 900 PNG, SVG | `posts/example-release-{square,wide}-{en,he}-*.png` | Social posts | Made per release with the generator |
| Title slide | 1920 × 1080 PNG, SVG | `posts/title-slide-{he,en}-1920x1080.png` | Talks | Drop into the first slide |
| README header snippet | Markdown/HTML | `templates/README-header.md` | Every repository | Paste and fill |
| Org profile README | Markdown | `templates/org-profile-README.md` | `HeOCR/.github` at `profile/README.md` | Copy, replace `BASE`, review the wording |
| Card header snippets | Markdown | `templates/model-card-header.md` | Hugging Face, Zenodo | Paste and fill |
| Generator | Python and Node | `tools/` | | See below |

## Making more

```
cd tools
python make_assets.py banner my-new-repo        # banners for a new repository: he/en, light/dark
python make_assets.py post v0.3.0 "One line about the release" --he "שורה אחת על הגרסה"
python make_assets.py                           # everything, from repos.json
node raster.js raster_jobs.json                 # the PNGs
```

Needs Python 3 with fontTools, and Node with Playwright for the PNGs. `tools/repos.json` holds every repository's one-line description, the badge labels, and the model and dataset entries. `tools/hbrand.py` is the drawing code: the mark, the box, the grid and outlined text.

## The one-line descriptions

The line on each social preview comes from `tools/repos.json`. Each repository's maintainer supplied its line through the lead on 2026-11-20 (the lead wrote `heocr-compute`'s). The Hebrew lines are new wording and need the owner's approval before the social previews are uploaded. To change a line, edit `repos.json` and run the two commands above.

The model card headers name the two published models, `heocr-modern-v1-tesseract-heb` and `heocr-oldprint-v1-tesseract-heb` (Apache-2.0). The htext header reads "CC0 (data) · MIT (code)", because every htext corpus published so far is CC0. When the first CC BY or CC BY-SA corpus ships, change it to "CC0, CC BY and CC BY-SA releases · code MIT".

## Platform limits

Checked on each platform's own documentation on 2026-11-20 unless noted.

| Place | What the documentation says | Source |
|---|---|---|
| GitHub social preview | PNG, JPG or GIF under 1 MB; at least 640 × 320, and 1280 × 640 for best display | [GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview), checked 2026-11-19 |
| GitHub profile picture (also organisations) | PNG, JPG or GIF; under 1 MB; smaller than 3000 × 3000; about 500 × 500 recommended | [GitHub Docs: profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference) |
| GitHub README, light and dark images | `<picture>` with `<source media="(prefers-color-scheme: dark)">` and a fallback `<img>` | [GitHub Blog](https://github.blog/developer-skills/github/how-to-make-your-images-in-markdown-on-github-adjust-for-dark-mode-and-light-mode/) |
| Zenodo community logo | "The logo must be smaller than 1MB." No format, shape or dimensions are stated | [Zenodo Help: edit community profile](https://help.zenodo.org/docs/communities/manage-community-settings/edit-profile/) |
| Hugging Face model card | `thumbnail` is a URL to an image used in social sharing. Light and dark images use `#hf-light-mode-only` / `#hf-dark-mode-only`, or the classes `dark:hidden` and `hidden dark:block` | [Hub docs: Model Cards](https://huggingface.co/docs/hub/model-cards), checked 2026-11-19 |
| Hugging Face organisation avatar | **No published size or format limit found.** A square PNG under 1 MB is supplied | Not documented where I looked |
| PyPI project description | The README is rendered from its text alone, so images need absolute URLs. **Whether PyPI keeps `<picture>` and `<source>` was not confirmed**; the snippet's fallback `<img>` is the light banner, so the page is right either way | A third-party guide ([Diamond Light Source template](https://diamondlightsource.github.io/python-copier-template/main/how-to/readme-images.html)), not PyPI's own documentation |

## File sizes

| Kind | Largest file | Limit in the brief |
|---|---|---|
| Banner PNG (2560 × 640) | under 40 KB | 300 KB |
| Social preview PNG | 62 KB | 1 MB |
| og:image PNG | 66 KB | |
| Avatar PNG | under 10 KB | 1 MB (GitHub, Zenodo) |
| Badge SVG | about 3 KB | |

PNGs were saved with Pillow's optimiser; oxipng was not available where this was made. Running `oxipng -o 4` over the folder would shave a little more and change nothing visible.

## Rules the assets keep

- **No figures, claims or comparisons.** No image carries a number other than a version in the release template and the page sizes above. Card headers never show accuracy.
- **No names** other than HeOCR; no people, no photos, no partner organisations. Tesseract is named on the model header because the model is a Tesseract model.
- **No real text.** The page motif is plain bars, not text.
- **No network.** Every SVG is paths only: no `<text>`, no font reference, no link, nothing fetched. The words are in each file's `<title>`.
- **Alt text** is in the snippets in Hebrew and English.
- **Contrast** uses the brand tokens: text on ground 18.7 light and 15.5 night; muted 6.3 and 6.8; the blue on white 6.3; white on the blue tag 6.3.

## Notes for the lead

1. **The existing English og:image** (`og-image-1200x630.png` on the site) shows the tag "h1 · 0.99" and the address `heocr.github.io`. The figure is decoration, but it reads as a score, and the brief now rules out numbers in any asset. `og/og-image-en-1200x630.png` is the same design with the tag "h1" and `heocr.org`. Replacing the live one is your call.
2. **Image URLs.** The snippets assume `https://raw.githubusercontent.com/HeOCR/heocr.github.io/main/design/asset-pack/…`. If the site serves `design/` from heocr.org, that address is better and stable; replace `BASE`.
3. **Links in the templates** to `/docs/`, `README.he.md` and the contributing guides are placeholders. I did not check that they exist.
4. **Org profile README wording** is new, in both languages, and needs the maintainer's review like any other Hebrew text.
5. **Badges are fixed images.** They state four facts; put them only on repositories where the fact holds.

## Sources

| Asset | Source | Licence |
|---|---|---|
| The mark, tokens, the box, the grid, the tag style | The brand handover (`design/brand-handover/`) | Project's own |
| Icon weight of the mark (avatar) | The Android design (`design/android/` in `heocr-desktop`) | Project's own |
| JetBrains Mono 500, 700; Noto Sans Hebrew 400, 500, 700 | `google/fonts`, instanced to static weights with fontTools; outlined into every image; the TTFs are in `tools/fonts/` for the generator only | SIL OFL 1.1 (`tools/fonts/OFL-*.txt`) |
| All layouts and wording | Made for this handover | Project's own |

## Not verified

- Nothing was uploaded to GitHub, PyPI, Hugging Face or Zenodo, so real cropping, tinting and rendering there are untested.
- The `<picture>` snippet was not rendered on GitHub or PyPI.
- Hebrew text is laid out by a small right-to-left pass in `hbrand.py`, which handles unpointed Hebrew with Latin words and digits. Pointed text or unusual punctuation would need a real shaping library.

---

`design[claude/claude-code#shay-macbook-m4]@heocr/opensource`
