# heocr.github.io

The one-page project site for HeOCR: https://heocr.github.io

It is static HTML with no build step: `index.html` and `rights.html` in English, and `he/index.html` and `he/rights.html` in Hebrew. A toggle at the top of each page switches language. GitHub Pages serves it from `main`.

## Benchmarks page

`benchmarks.html` and `he/benchmarks.html` are generated from one file, `benchmarks/results.json`. Do not edit the
two pages by hand. To update them, replace `results.json` with the file HeOCR's evaluation owner exports after a scored
run, then rebuild:

```
python3 scripts/build_benchmarks.py           # writes both pages (standard library only)
python3 scripts/build_benchmarks.py --check   # fails if a committed page does not match results.json
```

`results.json` holds only figures that may be published:
- figures on public references (Hebrew Wikisource);
- figures on generated documents with exact gold.

It never holds figures from private corpora, not even aggregates.
