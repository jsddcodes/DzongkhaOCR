# Models

Tesseract models kept in the repo. `src/ocr.py` uses a model from this folder
when its `.traineddata` file is here, and the system Tesseract install
otherwise.

## bod_uchen.traineddata

- **What:** Tesseract model for Tibetan Uchen script, fine-tuned from `bod` by
  the Buddhist Digital Resource Center (BDRC) on about 121,000 printed line
  images (Kangyur and Tengyur woodblock editions and other collections)
- **Source:** <https://huggingface.co/BDRC/Bod_uchen_tesseract>
- **License:** CC0 1.0 (public domain)
- **Downloaded:** 2026-10-27
- **SHA-256:** `c79403de88a64073914109242a5188e1ed0dbfbea65c0aa9b93896e4f02b5e3e`

Command-line use from the project root:

```bash
tesseract image.jpg stdout --tessdata-dir models -l bod_uchen --psm 6
```
