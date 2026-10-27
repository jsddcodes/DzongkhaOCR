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

Default preprocessing (grayscale + blur + adaptive threshold), `--psm 6`.
CER, lower is better.

| Category | Images | `dzo` | `bod` | `dzo+bod` | `bod_uchen` |
|---|---|---|---|---|---|
| Dzongkha, printed | 9 | 43.4% | 34.4% | 40.1% | 32.0% |
| Tibetan, printed | 1 | 6.4% | 0.0% | 0.0% | 3.2% |
| Handwriting | 2 | 98.0% | 89.8% | 85.5% | — |

`bod_uchen` is BDRC's Tesseract model fine-tuned from `bod` on ~121k printed
Tibetan lines (CC0, in `models/`). On the 8 textbook photos it averages 27.2%
against 35.0% for `bod`, winning on 6 of 8. It does badly on the stylized
alphabet chart (`printed_download.jpg` 70.5% against 29.5%). On `prayer.jpg`
it drops the leading `།` of each line (3.2%).

Dzongkha per image, `bod` (previous default grayscale + blur → current):

| Image | Before | Now | Photo conditions |
|---|---|---|---|
| `textbook_image5.jpeg` | 75.3% | 21.3% | Large shadow across the page |
| `textbook_image7.jpeg` | 76.8% | 23.2% | Shadow, curved page |
| `textbook_image4.jpeg` | 95.9% | 25.9% | Dark table in frame |
| `printed_download.jpg` | 17.2% | 29.5% | Clean digital chart |
| `textbook_image6.jpeg` | 30.0% | 33.5% | |
| `textbook_image.jpeg` | 38.5% | 36.4% | Highlighter, show-through |
| `textbook_image3.jpeg` | 84.1% | 36.5% | |
| `textbook_image1.jpg` | 37.4% | 49.0% | |
| `textbook_image2.jpg` | 53.1% | 54.2% | |

Findings so far:

- Photo conditions (shadows, background, curved pages) drive most errors.
- Adaptive thresholding rescues hard photos (75–96% → 21–37%) but costs
  accuracy on clean images (`printed_download` 17% → 30%,
  `textbook_image1` 37% → 49%). It won on average, so it is the default;
  the demo lets users switch clean-up off for clean digital images.
- Photo ablation (`src/ablate_preprocessing.py --group photo`, mean `bod`
  CER on Dzongkha): grayscale + blur 56.5%; + shadow removal 36.6%;
  + threshold 34.4%; + both 37.1%; + crop 56.4%; + deskew 60.8%.
- The original pipeline (upscale + grayscale + CLAHE + blur) was far worse on
  every printed image; CLAHE amplified show-through from the back of pages.
- Model ranking on Dzongkha so far: `bod_uchen` > `bod` > `dzo+bod` > `dzo`.
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
- BDRC `bod_uchen` model added (`models/`) and set as the demo default
- Streamlit demo live at dzongkhaocr.streamlit.app
- Summer report submitted to the agency

## Next

1. ~~**Handle real photos.**~~ Done 2026-10-27: adaptive threshold added to
   the default.
2. **Choose preprocessing per image** (re-test with more images). Picking the
   better of threshold / no threshold per image would cut mean CER from
   29.2% to 24.7% on the 10 printed images (`bod_uchen`). Tried 2026-10-27:
   - Lighting measures don't separate the cases (`textbook_image1` and
     `textbook_image2` look alike but need opposite settings).
   - Keeping the run with higher Tesseract confidence reached 27.3%, but
     picked wrong on 2 of 10, doubles runtime, and confidences are noisy
     (many near 0). Not adopted.
3. **Build the Tibetan benchmark.** Add 5–10 printed Chöke samples with
   checked transcripts: printed prayer books, pecha pages, and several fonts.
   `bod_uchen` was trained on pechas, so this is where it should be tested.
   Candidate source: openpecha/OCR-Tibetan_line_to_text_benchmark (~420k
   line images with text, mostly printed); its license is not yet confirmed.
4. **Confirm the model per category** (`bod_uchen`, `bod`, `dzo`) once both
   categories have enough images. If they differ, add a "text type" option
   (Dzongkha / Tibetan) to the demo.
5. ~~**Write photo guidelines.**~~ Done: [docs/photo_guidelines.md](docs/photo_guidelines.md).
6. ~~**Categorize errors.**~~ Done: `src/error_analysis.py`. For `bod_uchen` on
   Dzongkha (590 errors over 2,125 characters): consonants 44%, tsheg 15%,
   shad 11%, spaces 11%, stacked letters 8%, vowel signs 8%, digits and
   other 4%. Missed characters 36%, extra 25%, substituted 39%.
7. **Normalization rules.** Current: NFC, whitespace runs collapsed to one
   space. `evaluate.py` also reports `cer_nospace` (all spaces removed); it
   changes mean Dzongkha CER only from 32.0% to 31.5%, so spacing is not
   hiding real accuracy. Open: whether to treat tsheg before shad (`ང་།` vs
   `ང།`) and leading shad as equivalent.

Also checked 2026-10-27: PSM 3, 4, and 6 with every photo variant for
`bod_uchen` and `bod`. The current default (grayscale + blur + threshold,
PSM 6, 32.0%) was within 0.2 points of the best Dzongkha result (PSM 3,
31.8%), and PSM 3/4 were worse on the Tibetan sample, so PSM 6 stays.

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
