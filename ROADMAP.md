# Roadmap

Last updated: 2026-10-23. Deadline and required document types: **to be
confirmed** with the agency.

## Current baseline (measured 2026-10-23)

| Image | Best config | CER | Notes |
|---|---|---|---|
| `printed_download.jpg` | `bod`, current preprocessing, `--psm 4`/`6` | 41.8%* | Headings correct; large stylized vowel line missed; consonant rows partly garbled |
| `printed_download.jpg` | current default (`dzo`, `--psm 6`) | 50.0%* | |
| `painting.jpeg` | current default | 2433% | Scene text, not a document; background read as noise |

\* Against a draft corrected reference. The committed reference omits
`ཞ་ཟ་འ་ཡ` and `ར་ལ་ཤ་ས` (55.1% / 56.1% against it). Single image, so
indicative only.

Handwriting: earlier informal results (`bod` ~20%, `dzo` ~10%) have no
recorded metric or sample count. Not yet benchmarked.

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
- [ ] Ablate preprocessing one step at a time: original, upscale, grayscale,
      CLAHE, blur, thresholding, deskew
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
