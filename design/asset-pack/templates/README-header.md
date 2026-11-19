# README header snippet

Paste at the very top of a repository's `README.md`. Replace `REPO` with the repository's name (for example `heocr`) in the four image paths, write the one-line description, and keep only the badges and links that are true for that repository.

`BASE` is where the images are served from. Once the asset pack is merged, that is:

```
https://raw.githubusercontent.com/HeOCR/heocr.github.io/main/design/asset-pack
```

Use absolute URLs, as below: PyPI and Hugging Face only see the README's text, not the files beside it.

## English first

```html
<p align="center">
  <a href="https://heocr.org/en/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="BASE/banners/REPO/REPO-en-dark.png">
      <source media="(prefers-color-scheme: light)" srcset="BASE/banners/REPO/REPO-en-light.png">
      <img src="BASE/banners/REPO/REPO-en-light.png" width="640" alt="HeOCR: Hebrew text out of any document. REPO.">
    </picture>
  </a>
</p>

<p align="center">One line saying what this repository is.</p>

<p align="center">
  <a href="https://github.com/HeOCR/REPO/actions"><img src="https://img.shields.io/github/actions/workflow/status/HeOCR/REPO/ci.yml?style=flat-square&label=CI" alt="CI status"></a>
  <a href="https://pypi.org/project/heocr/"><img src="https://img.shields.io/pypi/v/heocr?style=flat-square" alt="PyPI version"></a>
  <img src="BASE/badges/hebrew-first-en.svg" height="20" alt="Hebrew-first">
  <img src="BASE/badges/offline-en.svg" height="20" alt="Works offline">
  <img src="BASE/badges/apache-2-en.svg" height="20" alt="Licence: Apache-2.0">
</p>

<p align="center">
  <a href="https://heocr.org/en/">Website</a> ·
  <a href="https://heocr.org/en/docs/">Docs</a> ·
  <a href="https://pypi.org/project/heocr/">PyPI</a> ·
  <a href="README.he.md">עברית</a>
</p>
```

## Hebrew first

```html
<p align="center">
  <a href="https://heocr.org/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="BASE/banners/REPO/REPO-he-dark.png">
      <source media="(prefers-color-scheme: light)" srcset="BASE/banners/REPO/REPO-he-light.png">
      <img src="BASE/banners/REPO/REPO-he-light.png" width="640" alt="HeOCR: טקסט עברי מכל מסמך. REPO.">
    </picture>
  </a>
</p>

<p align="center" dir="rtl">שורה אחת שאומרת מה המאגר הזה.</p>

<p align="center">
  <img src="BASE/badges/hebrew-first-he.svg" height="20" alt="עברית תחילה">
  <img src="BASE/badges/offline-he.svg" height="20" alt="עובד בלי אינטרנט">
  <img src="BASE/badges/apache-2-he.svg" height="20" alt="רישיון: Apache-2.0">
</p>

<p align="center" dir="rtl">
  <a href="https://heocr.org/">האתר</a> ·
  <a href="https://heocr.org/docs/">תיעוד</a> ·
  <a href="https://pypi.org/project/heocr/">PyPI</a> ·
  <a href="README.en.md">English</a>
</p>
```

## Notes

- **Light and dark.** GitHub picks the `<source>` by the reader's theme. Where `<picture>` is not supported, the `<img>` fallback shows the light banner, which has its own white ground and reads on a dark page too.
- **Hugging Face** does not use `<picture>`. In a model card use two images with its classes instead:
  `<img class="dark:hidden" src="BASE/banners/REPO/REPO-en-light.png" alt="…">` and `<img class="hidden dark:block" src="BASE/banners/REPO/REPO-en-dark.png" alt="…">`.
- **The banner is 1280 × 320 at 2×.** `width="640"` shows it at half size, sharp on dense screens; raise it to 800 if the README is wide.
- **Badges.** Use shields.io for anything that changes (CI, version, downloads) with `style=flat-square`, which is 20 px high with square corners like ours. Use the HeOCR badges only for the four fixed facts, and only where true: "offline" does not belong on `heocr-review` or `heocr-compute`; "open data · CC0" belongs on data repositories whose licence is CC0.
- **Put dynamic badges first**, then ours, in one row. Do not recolour shields badges to the brand blue: their colours carry meaning (passing, failing).
- **Links** (`/docs/`, `README.he.md`) are placeholders; point them at what exists.
