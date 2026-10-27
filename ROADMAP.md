# Roadmap

Last updated: 2026-10-27. Independent project, continued after a GovTech
summer internship (report submitted). No external deadline.

## Current baseline (measured 2026-10-27)

Default preprocessing (grayscale + blur), `--psm 6`. Three printed images,
so indicative only.

| Image | `dzo` | `bod` | Notes |
|---|---|---|---|
| `textbook_image.jpeg` | 43.4% | 38.5% | Modern Dzongkha, photographed; highlighted heading missed |
| `printed_download.jpg` | 27.9% | 17.2% | Alphabet chart; large stylized lines are the main errors |
| `prayer.jpg` | 6.4% | 0.0% | Classical Tibetan, so it favors `bod` |
| Mean | 25.9% | 18.6% | `dzo+bod` 18.9% |

`printed_download.txt` was completed on 2026-10-27 (two consonant rows had
been missing); earlier scores for that image were measured against the
incomplete reference.

Preprocessing ablation (`src/ablate_preprocessing.py`): the old default
(upscale + grayscale + CLAHE + blur) averaged 88–97% CER, against 34–38% for
the original image. CLAHE alone roughly doubled errors on the textbook photo,
probably by amplifying text showing through from the back of the page.
Grayscale + blur had the lowest mean and became the default.

Handwriting (`handwriting.JPG`, `written_image.jpg`): 62–95% CER at best.
Tesseract is not usable for handwriting. Scene text (`painting.jpeg`) fails.

## Done

- Environment verified; one OpenCV package (`opencv-python` 5.0.0.93);
  `requirements.txt` and `packages.txt` filled in; README written
- Batch evaluation (`src/evaluate.py`): every labeled image × `dzo`/`bod`/`dzo+bod`
  × PSM × preprocessing, NFC + whitespace normalization, raw outputs and CSV
  per timestamped run, document/handwriting/scene scored separately
- Preprocessing ablation; default changed to grayscale + blur
- Streamlit demo live at dzongkhaocr.streamlit.app: sample images, language
  and clean-up selectors, error handling, demo-only warning
- Summer report submitted to the agency

## Next: benchmark data

The benchmark has one real Dzongkha page. Every decision below depends on more.

- [x] Fix `ground_truth/printed_download.txt`: add the missing consonant rows
- [ ] Add 5–10 printed modern Dzongkha crops with checked transcripts. Aim for
      variety: news, textbook, government notice, several fonts, scans and photos
- [ ] Document normalization rules (NFC, whitespace, tsheg/shad handling)

## Then: tuning

- [ ] Choose a default language config (`dzo`, `bod`, or `dzo+bod`) using
      Dzongkha pages only (`prayer.jpg` is Tibetan)
- [ ] Ablate new candidate steps: thresholding, deskew
- [ ] Try PSM and DPI settings; consider per-line segmentation for charts and tables
- [ ] Categorize errors: stacked characters, similar glyphs, spacing,
      punctuation, numerals, stylized fonts

## Later: train Tesseract on Dzongkha

The largest likely accuracy gain. Can use synthetic data, so it does not
depend on an agency corpus.

- [ ] Collect openly licensed Dzongkha text and Dzongkha fonts
- [ ] Render synthetic line images and fine-tune from `dzo` or `bod` (tesstrain)
- [ ] Compare against `dzo` and `bod` on the benchmark. Keep benchmark text
      out of the training data

## Demo

- [ ] Keep the demo's samples and defaults in line with benchmark results
- [ ] After pushing changes to `src/ocr.py` or `src/preprocessing.py`, reboot
      the Streamlit Cloud app (it can keep stale modules)

## Parked

- Handwriting: Tesseract can't read it; would need a different model and data
- PaddleOCR: revisit only if a Tibetan/Dzongkha recognition model appears
- Agency corpus: none was provided; revisit if offered
