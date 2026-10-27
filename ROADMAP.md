# Roadmap

Last updated: 2026-10-27. Independent project, continued after a GovTech
summer internship (report submitted). No external deadline.

## Goal

OCR for printed text in the Tibetan script as used in Bhutan, in two languages:

- **Dzongkha**: everyday documents, textbooks, notices
- **Classical Tibetan (Chöke)**: Buddhist prayers, scriptures, and study texts

Both share one script, so they share one pipeline, but they are scored as
separate categories (`dzongkha`, `tibetan`) because spelling, vocabulary, and
page layouts (for example pecha pages) differ.

## Current baseline (measured 2026-10-27)

Default preprocessing (grayscale + blur), `--psm 6`. CER, lower is better.

| Category | Images | `dzo` | `bod` | `dzo+bod` |
|---|---|---|---|---|
| Dzongkha, printed | 9 | 59.7% | 56.5% | 58.7% |
| Tibetan, printed | 1 | 6.4% | 0.0% | 0.0% |
| Handwriting | 2 | 84.5% | 87.5% | 84.2% |

Dzongkha per image (`dzo` / `bod`):

| Image | `dzo` | `bod` | Photo conditions |
|---|---|---|---|
| `printed_download.jpg` | 27.9% | 17.2% | Clean digital chart |
| `textbook_image6.jpeg` | 44.2% | 30.0% | |
| `textbook_image1.jpg` | 40.8% | 37.4% | |
| `textbook_image.jpeg` | 43.4% | 38.5% | Highlighter, show-through |
| `textbook_image2.jpg` | 57.3% | 53.1% | |
| `textbook_image5.jpeg` | 78.6% | 75.3% | Large shadow across the page |
| `textbook_image7.jpeg` | 75.7% | 76.8% | Shadow, curved page; whole lines skipped |
| `textbook_image3.jpeg` | 84.4% | 84.1% | |
| `textbook_image4.jpeg` | 84.5% | 95.9% | Dark table in frame; 25–37% without preprocessing |

Findings so far:

- Photo conditions (shadows, background, curved pages) drive most errors.
  On clean images the text is read well.
- Grayscale + blur helps some photos and badly hurts others
  (`textbook_image6` 96% → 30%, `textbook_image4` 25% → 96%).
- The old default (upscale + grayscale + CLAHE + blur) was far worse on
  every printed image; CLAHE amplified show-through from the back of pages.
- `bod` is slightly ahead of `dzo` on Dzongkha, but not on every image.
- The one Tibetan sample is a clean digital render, so its 0% says little
  about real prayer books or pechas.
- Tesseract cannot read handwriting. Scene text (`painting.jpeg`) fails.

## Done

- Environment verified; one OpenCV package (`opencv-python` 5.0.0.93);
  `requirements.txt` and `packages.txt` filled in; README written
- Batch evaluation (`src/evaluate.py`) with per-category scores, raw outputs,
  and a CSV per timestamped run
- Preprocessing ablation (`src/ablate_preprocessing.py`)
- 9 printed Dzongkha references, including 8 textbook photos;
  `printed_download.txt` completed
- Streamlit demo live at dzongkhaocr.streamlit.app
- Summer report submitted to the agency

## Next

1. **Handle real photos.** Add shadow-tolerant steps to the ablation:
   adaptive thresholding, deskew, and cropping to the page. Run on all
   Dzongkha and Tibetan images. Pick the default from the results; consider
   choosing preprocessing per image if no single setting wins.
2. **Build the Tibetan benchmark.** Add 5–10 printed Chöke samples with
   checked transcripts: printed prayer books, pecha pages, and several fonts.
3. **Choose a language model per category** (`dzo`, `bod`, or `dzo+bod`) once
   both categories have enough images. If they differ, add a "text type"
   option (Dzongkha / Tibetan) to the demo.
4. **Write photo guidelines** for capturing pages: flat, even light, no
   shadow, page fills the frame, camera straight above.
5. **Categorize errors**: stacked characters, similar glyphs, spacing,
   tsheg/shad punctuation, numerals, stylized fonts.
6. Document normalization rules (NFC, whitespace, tsheg/shad handling).

## Later: train Tesseract

The largest likely accuracy gain. Can use synthetic data, so it does not
depend on an agency corpus.

- [ ] Collect openly licensed text in both languages (Dzongkha prose;
      Tibetan Buddhist e-texts) and fonts used in Bhutanese print and pechas
- [ ] Render synthetic line images and fine-tune from `bod` or `dzo` (tesstrain)
- [ ] Compare against `dzo` and `bod` on both categories. Keep benchmark text
      out of the training data

## Demo upkeep

- [ ] Keep samples and defaults in line with benchmark results
- [ ] After pushing changes to `src/ocr.py` or `src/preprocessing.py`, reboot
      the Streamlit Cloud app (it can keep stale modules)

## Parked

- Handwriting: needs a different model and data
- PaddleOCR: revisit only if a Tibetan/Dzongkha recognition model appears
- Agency corpus: none was provided; revisit if offered
