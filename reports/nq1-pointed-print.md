# Pointed print (niqqud) photographed by phone (NQ1): results at heocr 0.2.0rc1

*Draft for review, 2026-11-20.*

**The set.**
- **Pages:** 25 pages of modern pointed Hebrew: poetry, Tanakh passages, and prose pointed by Dicta's nakdan.
- **Typesetting:** by us, in open fonts, two of them held out from all training.
- **Capture:** printed, then photographed twice per page in each of two sessions, 101 photos in all.
- **Held out:** registered before printing and scored once.

**Results**, all photos, character error:

| reader | niqqud counted | letters only | vowel marks found |
|---|---|---|---|
| heocr (heocr_modern_v1) | 56.0% | 30.1% | 0% |
| heocr with heocr_oldprint_v1 | 58.3% | 33.8% | 0% |
| HeOCR oldprint-v1 inherits R7 checkpoint-selection exposure to 7,092 development rows from two sources now reserved in line_verify. Comparisons on those sources are selection-exposed. | | | |
| heocr with stock Tesseract's model | 45.8% | 29.5% | 24% |
| Tesseract (tessdata_best heb) | 43.7% | 25.8% | 25% |
| Tesseract (tessdata_fast heb) | 40.3% | 25.7% | 33% |

**What this means.**
- **HeOCR's models write no niqqud.** heocr_modern_v1 wrote none at all; heocr_oldprint_v1 wrote 238 marks in about
  52,000 letters.
- **Pointed text comes out unpointed.** On the letters alone, our model matches stock Tesseract's model inside heocr.
- **Every reader struggles:** no reader finds more than a third of the vowel marks.
- **Next:** pointed print is a gap for the next training round, and the model cards now say so.

**Caveats:**
- modern pointed print in open fonts, not old pointed books;
- 25 pages, one printer, one phone.
