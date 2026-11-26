# Prompt for whoever takes this in

Copy the text below to the developer or coding agent.

---

You are taking over the HeOCR site redesign (the "Bounding Box" brand). The complete handover package is in `~/temp/heocr-brand-handover`. Start with its `README.md`.

**Important: `~/temp` is a transient location and may be wiped at any time.** Before doing anything else, copy the whole folder into the HeOCR site repository (the one that publishes heocr.github.io) under `design/brand-handover/`, commit it, push it, and confirm the push succeeded. From then on work only from the copy in the repository, and never rely on `~/temp` again.

Then:

1. Read `README.md`, `BRAND.md` and `site/MARKUP.md`.
2. Port the design into the site's Python generator scripts. Use `site/site.css` and `site/theme.js` as they are, call `site/hero_chart.py` for the Benchmarks hero chart, and emit the markup patterns shown in `site/*.html`. Keep all method, rights and licence wording unchanged, and keep every number coming from the JSON files.
3. Add the logo and favicon files from `logo/` to the site and wire them into every page.
4. Compare your generated pages with the maintained site at 1280 px and 375 px in both themes and languages. The rights-page references are in `reference/pages/`. Run the checks in `README.md`.
5. Open a pull request, and list anything you could not match or chose to change.

The open items (verdict field in `results.json`, run date field, new wording) are in `README.md`.
