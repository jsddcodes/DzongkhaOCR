# Roadmap

Last updated: 2026-10-27. Deadline and required document types: **to be
confirmed** with the agency.

## Current baseline (measured 2026-10-27)

Default preprocessing (grayscale + blur), `--psm 6`. Three printed images,
so indicative only.

| Image | `dzo` | `bod` | Notes |
|---|---|---|---|
| `textbook_image.jpeg` | 43.4% | 38.5% | Modern Dzongkha, photographed; highlighted heading missed |
| `printed_download.jpg` | 41.1% | 39.3% | Alphabet chart; large stylized lines are the main errors |
| `prayer.jpg` | 6.4% | 0.0% | Classical Tibetan, so it favors `bod` |
| Mean | 30.3% | 25.9% | `dzo+bod` 25.3% |

Preprocessing ablation (`src/ablate_preprocessing.py`): the old default
(upscale + grayscale + CLAHE + blur) averaged 88–97% CER, against 34–38% for
the original image. CLAHE alone roughly doubled errors on the textbook photo,
probably by amplifying text showing through from the back of the page.
Grayscale + blur had the lowest mean and became the default.

Handwriting (`handwriting.JPG`, `written_image.jpg`): 62–95% CER at best.
Tesseract is not usable for handwriting. Scene text (`painting.jpeg`) fails.

## Phase 1: Reproducible baseline

- [x] Verify environment and Tesseract language packs (`bod`, `dzo`)
- [x] Run one image end to end through the existing pipeline
- [x] First `dzo` vs `bod` × preprocessing × PSM comparison
- [ ] Fix `ground_truth/printed_download.txt` (missing 8 consonants) after owner review
- [ ] Uninstall one of `opencv-python` / `opencv-contrib-python`
- [x] Populate `requirements.txt` from the working environment
- [x] Fill in `README.md` with setup and run instructions

## Phase 2: Benchmark

- [ ] Write human-verified transcripts for the remaining `test_data/` images:
      `printed_text`, `website_screenshot`, `written_image`, `handwriting`,
      `low_quality_handwriting`
- [ ] Add more printed and scanned document samples (multiple fonts, older or
      noisy pages)
- [x] Generalize `evaluate.py`: loop over every image with a reference, apply
      fixed normalization, report CER/WER/exact match/runtime, and save raw
      outputs plus a results CSV to `results/` with timestamps
- [ ] Document normalization rules (NFC, whitespace, tsheg/shad handling)
- [x] Keep document, scene-text, and handwriting scores in separate categories

## Phase 3: Tuning

- [ ] Choose a default language config (`bod`, `dzo`, or `dzo+bod`) from the benchmark
- [x] Ablate the existing steps one at a time (`src/ablate_preprocessing.py`):
      original, upscale, grayscale, CLAHE, blur, full, full minus each step
- [ ] Ablate new candidate steps: thresholding, deskew
- [ ] Try PSM and DPI settings; consider per-line segmentation for charts and tables
- [ ] Categorize errors: stacked characters, similar glyphs, spacing,
      punctuation, numerals, stylized fonts

## Phase 4: Prototype UI

- [x] Streamlit: remove the duplicate `preprocess_image` call
- [ ] Add language/preprocessing selectors that match the benchmarked options
- [x] Handle invalid or unreadable uploads gracefully
- [ ] Verify the app end to end with `streamlit run`

## Phase 5: Data and models (conditional)

- [ ] Confirm agency corpus: format, size, image/transcript pairing, printed
      vs handwritten, permissions, retention, and whether data may leave the machine
- [ ] Decide whether fine-tuning Tesseract on Dzongkha is feasible before the deadline
- [ ] Revisit PaddleOCR only if a compatible Tibetan/Dzongkha recognition model is confirmed

## Phase 6: Report

- [ ] Technical report: pipeline, dataset, metrics, failure examples,
      limitations, next-phase recommendations

## Open questions

- Is handwriting required for the first release?
- What is the exact deadline and deliverable?
- Will the agency corpus arrive, and under what terms?
