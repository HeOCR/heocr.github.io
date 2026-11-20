# heocr 0.2.0rc1: release gate results (RC2)

*Draft for review, 2026-11-20.*

**What was tested.**
- **The release candidate:** heocr 0.2.0rc1, which reads scans with HeOCR's own model, `heocr_modern_v1`, by default.
  It was installed from the published PyPI package.
- **The rule:** a document type is *supported* when heocr is no worse than every other open tool by more than a fixed
  margin, on documents generated after the code was frozen. A check on real documents can still hold a type back.
- **Registration:** the rules, readers and seed were registered before the documents existed, and the run was scored
  once.

**Verdict: 9 of 10 document types are supported.**
- **Supported:** Word (.docx and .doc), PDFs with a good, reversed or broken text layer, two-page spreads, and scanned
  tables.
- **Newly supported:** scans under a wrong OCR layer (T4) and image-only scans (T5). Both failed in the first release
  candidate.
- **Held back: PDFs with text drawn as images (T6).** On real documents, heocr reversed more amounts than stock
  Tesseract (0.45% against at most 0.27%).

**What our own model adds**, on the same generated scans, with the same pipeline:
- **Character errors:** 1.3% against 3.3% with stock Tesseract's model on scans, and 0.4% against 1.4% on scanned
  tables.
- **Missed numbers:** 5.2% against 22.7% on scans.

**Read this with the real-photo results beside it.** The test documents are drawn by the same generators heocr is
developed against, so they favour it. On real phone photos of printed pages (PS-v1), the model's gain does not hold.

Details: the Benchmarks page (Documents by format) and `benchmarks/results.json`.
