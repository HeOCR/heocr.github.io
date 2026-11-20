# Printed pages photographed by phone (PS-v1): results at heocr 0.2.0rc1

*Draft for review, 2026-11-20.*

**The set.**
- **Pages:** 12 pages of printed modern Hebrew, legislation and prose, typeset by us from public-domain texts.
- **Capture:** printed, then photographed by the maintainer with three phones in four conditions: flat, at an angle,
  in low light, and crumpled.
- **Held out:** no model was trained, tuned or chosen on them. The set was registered before any photo was taken and
  scored once.

**Results** (character error, lower is better):
- **Headline, main phone, flat:** heocr 14.1%, plain Tesseract (tessdata_best) 13.1%. The difference is not
  significant (+1.0 point, 95% interval −0.3 to +2.6).
- **Flat, all phones:** heocr is 3.6 points worse than plain Tesseract (interval +1.5 to +6.3).
- **Angle, low light, crumpled:** the differences are not significant. heocr is better at an angle and worse in low
  light, with wide intervals.
- **Our own model inside heocr** adds nothing on these photos: within about a point of stock Tesseract's model in
  every condition.
- **Numbers:** heocr finds more of them. On the headline photos, 76.8% of numbers against 69.9%.

**What this means.** The gains seen on generated scans don't carry over to real phone photos. Phone photos remain hard
for every reader tested, with character errors of 13–44% depending on conditions. heocr doesn't correct perspective.

**Caveats:**
- this is not a sample of real-world documents: one printer, three phones, our typesetting;
- with 12 pages, intervals are wide.
