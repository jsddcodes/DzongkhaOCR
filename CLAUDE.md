# CLAUDE.md

Dzongkha OCR prototype: recognize printed Tibetan-script text as used in
Bhutan, in two languages: Dzongkha (everyday documents) and Classical Tibetan
(Chöke, used for Buddhist prayers and study). Uses Tesseract (via
`pytesseract`), OpenCV preprocessing, and a Streamlit demo UI.
Goal is a reproducible baseline with honest CER-based evaluation, not a
production system. See `ROADMAP.md` for status and next steps.

## Environment

- Use `paddleocr_env/bin/python` (Python 3.11.15). It is the only environment
  with all dependencies. The system `python3` (3.14) lacks OpenCV and jiwer.
- Tesseract 5.5.2 at `/opt/homebrew/bin/tesseract`; `bod` and `dzo` traineddata
  installed in `/opt/homebrew/share/tessdata/`.
- Key packages: pytesseract 0.3.13, opencv-python 5.0.0.93, jiwer 4.0.0,
  streamlit 1.60.0, pillow 12.3.0, paddleocr 3.7.0 / paddlepaddle 3.3.1 /
  paddlex 3.7.2.
- Only `opencv-python` is installed (`opencv-contrib-python` was removed
  2026-10-27). Don't install both; they share the `cv2` package.
- `requirements.txt` pins the app's packages; `packages.txt` lists the apt
  packages Streamlit Cloud needs (Tesseract, `dzo`/`bod`, OpenCV libs).

## Running

Always run from the project root with `PYTHONPATH=src`. Modules use bare
imports (`from ocr import ...`), while data paths are relative to the root:

```bash
PYTHONPATH=src paddleocr_env/bin/python src/evaluate.py
PYTHONPATH=src paddleocr_env/bin/python src/ocr.py
PYTHONPATH=src paddleocr_env/bin/streamlit run src/streamlit_app.py
tesseract test_data/printed_download.jpg stdout -l bod --psm 6
```

## Layout

- `src/preprocessing.py`: `preprocess_image(path)` defaults to grayscale +
  3×3 Gaussian blur + adaptive threshold (chosen from the 2026-10-27 photo
  ablation). Optional flags: `upscale`, `crop_page`, `remove_shadows`,
  `clahe`, `deskew`. Returns a grayscale array, or RGB if every step is off.
  When adding a step, also add it to the all-off call in `ocr.extract_text`
  (`preprocess=False` must mean the original image).
- `src/ocr.py`: `extract_text(path)` preprocesses, then runs Tesseract with
  `lang="dzo"` and `--psm 6`.
- `src/evaluate.py`: batch CER/WER over every `ground_truth/` + `test_data/`
  pair across a lang × PSM × preprocessing grid. Each run writes
  `results/eval_<timestamp>/` (results.csv + raw outputs). Scene images are
  listed in `CATEGORIES` and scored separately.
- `src/ablate_preprocessing.py`: CER per preprocessing variant on printed
  documents, mean per category. `--group base` (original four steps, each
  alone and full minus each), `--group photo` (photo steps added to the
  default), or `all`. Writes `results/ablation_<timestamp>/`.
- `src/streamlit_app.py`: upload, preview, OCR, download.
- `src/test_paddle.py`: PaddleOCR experiment. Fails with
  `No models are available for lang=bod`. Don't keep guessing language codes.
- `test_data/`: evaluation images. `images/`: misc samples.
- `ground_truth/<image_stem>.txt`: human reference transcripts (UTF-8), named
  after the image they describe.
- `results/`: outputs. Keep raw OCR outputs; don't overwrite previous runs.

## Evaluation conventions

- Primary metric is CER. Normalize both sides the same way before scoring
  (Unicode NFC, collapse whitespace) and keep raw output alongside.
- Compare configurations (`dzo`/`bod`, preprocessing variant, PSM) on identical
  images. With so few labeled images, treat differences as hints only.
- Ground truth must be human-verified. Don't edit or replace reference
  transcripts without the owner's confirmation.
- Score Dzongkha and Tibetan documents as separate categories
  (`CATEGORIES` in `src/evaluate.py`; unlisted images count as `dzongkha`).
  Add every new Tibetan image there as `tibetan`. Never pool the two when
  choosing a model; `bod` has a built-in advantage on Tibetan text.
- `painting.jpeg` is scene text (painted rock), and handwriting is its own
  category. Report both separately from the document benchmark.

## Rules

- Data privacy: never send agency or government documents to external services
  or AI tools without explicit authorization. Keep corpus data local.
- Make small, testable changes and report exact commands and results.
- Don't claim accuracy improvements without a measured CER comparison.
- Preprocessing can damage stacked characters and fine vowel marks, so test
  each transform on its own.
