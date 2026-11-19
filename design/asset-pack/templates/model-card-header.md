# Model and dataset card headers

`BASE` = `https://raw.githubusercontent.com/HeOCR/heocr.github.io/main/design/asset-pack`

## Hugging Face model card

In the YAML block at the top of the model's `README.md`:

```yaml
thumbnail: BASE/cards/model-MODEL-en-1280x640.png
```

At the top of the card's text:

```html
<img src="BASE/cards/model-MODEL-en-1280x640.png" width="640" alt="HeOCR model MODEL: Hebrew OCR model for Tesseract. Licence: Apache-2.0.">
```

## Zenodo record

Zenodo's description field takes limited HTML. Add the image by its absolute URL as the first line of the description, or upload the PNG with the record's files so it is archived with it:

```html
<p><img src="BASE/cards/dataset-htext-en-1280x640.png" alt="HeOCR dataset htext: Hebrew text dataset release. Licence: CC0-1.0." width="640"></p>
```

## Rules for these images

- No accuracy figures, scores or comparisons, ever. An image cannot be corrected when results change.
- Make one per model or dataset with the generator: add an entry to `tools/repos.json` under `models` or `datasets` and run `python make_assets.py`.
- The licence chip must match the record's licence field.
