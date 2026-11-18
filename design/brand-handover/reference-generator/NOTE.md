# Reference generator: read, don't run

These are the scripts that produced the files in `site/`. They are here so you can see exactly how each piece of markup was derived from `results.json`: the grouped tables, the format-specific last column, the release-gate summary, the hero chart caption.

They are not production code and will not run as they are:

- They read the old pages from hard-coded paths and lift the fixed wording out of them with regular expressions.
- `brand.py` and `site_b.py` patch `build.py` at import time.
- They also wrote design-canvas files that are not part of this package.

| File | What to look at |
|---|---|
| `build.py` | `docs_tables()`, `hist_table()`, `gate_block()`, `hero()`, `legend()`, `cell_html()`: the markup builders. |
| `site_b.py` | The header with the logo, the boxed page title, the htext and rights page shells. |
| `brand.py` | The three logo drawings on a 48-unit grid (`MARKS`); Logo 1 is the chosen one. |
| `brand_b.css`, `brand_b_layer.css` | The token block and the brand layer that were merged into `site/site.css`. |

The hero chart generator you should actually use is `site/hero_chart.py`, which is self-contained.
