# CLAUDE.md

Dzongkha OCR prototype: recognize Dzongkha text from document images using
Tesseract (via `pytesseract`), OpenCV preprocessing, and a Streamlit demo UI.
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
- Known issue: `opencv-python` and `opencv-contrib-python` are both installed
  and can conflict. Keep only one.
- `requirements.txt` is currently empty.

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

- `src/preprocessing.py`: `preprocess_image(path)` does 2× upscale, grayscale,
  CLAHE, and a 3×3 Gaussian blur, returning a grayscale array.
- `src/ocr.py`: `extract_text(path)` preprocesses, then runs Tesseract with
  `lang="dzo"` and `--psm 6`.
- `src/evaluate.py`: CER (jiwer) for a single hard-coded image/reference pair.
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
- `painting.jpeg` is scene text (painted rock), not a document. Report it
  separately rather than in the document benchmark.

## Rules

- Data privacy: never send agency or government documents to external services
  or AI tools without explicit authorization. Keep corpus data local.
- Make small, testable changes and report exact commands and results.
- Don't claim accuracy improvements without a measured CER comparison.
- Preprocessing can damage stacked characters and fine vowel marks, so test
  each transform on its own.
