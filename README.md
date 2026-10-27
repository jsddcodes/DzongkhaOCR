# Dzongkha OCR

A prototype for recognizing printed text in the Tibetan script as used in
Bhutan: Dzongkha for everyday documents, and Classical Tibetan (Chöke) for
Buddhist prayers and study texts. It uses
[Tesseract](https://github.com/tesseract-ocr/tesseract) (through
`pytesseract`), OpenCV preprocessing, and a Streamlit demo UI.

The goal is a reproducible baseline with honest evaluation based on
character error rate (CER). It is not a production system. See
[ROADMAP.md](ROADMAP.md) for status and next steps.

## How it works

```
image → preprocessing (OpenCV) → Tesseract (bod_uchen / bod / dzo, --psm 6) → text
```

1. **Preprocessing** ([src/preprocessing.py](src/preprocessing.py)):
   grayscale, a 3×3 Gaussian blur, and an adaptive threshold (black and white,
   tolerant of shadows) by default. Upscaling, CLAHE, shadow removal, page
   cropping, and deskew are available but off (see [ROADMAP.md](ROADMAP.md)).
2. **OCR** ([src/ocr.py](src/ocr.py)): Tesseract with page segmentation
   mode 6 (a single uniform block of text) and one of three language models:
   `bod_uchen` (BDRC's Tibetan Uchen model, included in [models/](models/)),
   `bod`, or `dzo`. The demo defaults to `bod_uchen`.
3. **Evaluation** ([src/evaluate.py](src/evaluate.py)): scores every image
   that has a human-verified reference transcript across language models,
   PSM settings, and preprocessing on/off, using CER computed with `jiwer`.

## Setup

Tested on macOS (Apple Silicon) with Python 3.11 and Tesseract 5.5.

### 1. Tesseract and language data

```bash
brew install tesseract tesseract-lang   # tesseract-lang includes dzo and bod
tesseract --list-langs                  # should list both dzo and bod
```

`dzo` is Dzongkha and `bod` is Tibetan. They share a script, and both are
worth comparing. The third model, `bod_uchen`, ships with the repo in
`models/` (CC0, from the Buddhist Digital Resource Center), so it needs no
installation; see [models/README.md](models/README.md).

### 2. Python environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install pytesseract opencv-python jiwer streamlit pillow
```

Versions known to work: pytesseract 0.3.13, opencv-python 5.0.0.93,
jiwer 4.0.0, streamlit 1.60.0, pillow 12.3.0. `requirements.txt` has not
been filled in yet.

Install only one of `opencv-python` and `opencv-contrib-python`. Having
both installed causes conflicts.

## Usage

Run all commands from the project root with `PYTHONPATH=src`, because the
modules import each other by bare name and data paths are relative to the root.

```bash
# OCR a single image (currently hard-coded to images/sample.jpeg)
PYTHONPATH=src python src/ocr.py

# Save the preprocessed image to results/preprocessed.png
PYTHONPATH=src python src/preprocessing.py

# Batch evaluation: every labeled image × dzo/bod/dzo+bod × PSM 4/6 × preprocessing on/off
# Writes results.csv and raw outputs to a new results/eval_<timestamp>/ folder
PYTHONPATH=src python src/evaluate.py
PYTHONPATH=src python src/evaluate.py --langs bod --psms 6   # a smaller grid

# Error breakdown by character type (default: bod_uchen, default preprocessing)
PYTHONPATH=src python src/error_analysis.py

# Preprocessing ablation: each clean-up step on its own, on printed documents
PYTHONPATH=src python src/ablate_preprocessing.py

# Demo UI: upload an image, preview it, extract text, download the result
PYTHONPATH=src streamlit run src/streamlit_app.py

# Run Tesseract directly to compare configurations
tesseract test_data/printed_download.jpg stdout -l bod --psm 6
```

## Project layout

```
src/
  preprocessing.py   preprocess_image(path) → grayscale array
  ocr.py             extract_text(path) → recognized text
  evaluate.py        batch CER evaluation over all labeled images
  ablate_preprocessing.py  CER for each preprocessing step on its own
  error_analysis.py  errors by character type (consonant, stacked, tsheg, ...)
docs/
  photo_guidelines.md  how to photograph pages for OCR and the test set
models/              Tesseract models kept in the repo (bod_uchen)
  streamlit_app.py   demo UI
  test_paddle.py     PaddleOCR experiment (see Known limitations)
test_data/           evaluation images
ground_truth/        reference transcripts, named <image_stem>.txt (UTF-8)
images/              miscellaneous samples
results/             OCR outputs and preprocessed images
```

## Evaluation

The primary metric is **CER**. When adding to the benchmark:

- Name each reference transcript after its image, for example
  `test_data/printed_download.jpg` → `ground_truth/printed_download.txt`.
- Reference transcripts must be checked by a human.
- Normalize OCR output and reference the same way (Unicode NFC, collapse
  whitespace) before scoring, and keep the raw output too.
- Compare configurations (`dzo` vs `bod`, preprocessing, PSM) on the same images.
- Report scene text (for example `painting.jpeg`, a painted rock) and handwriting
  separately from printed documents.

### Current results

Mean CER, default preprocessing (grayscale + blur + adaptive threshold),
`--psm 6`. The image sets are small, so these numbers are **hints only**.
Per-image results are in [ROADMAP.md](ROADMAP.md).

| Category | Images | `dzo` | `bod` | `bod_uchen` |
|---|---|---|---|---|
| Dzongkha, printed (mostly textbook photos) | 9 | 43.4% | 34.4% | 32.0% |
| Classical Tibetan, printed (one clean digital prayer) | 1 | 6.4% | 0.0% | 3.2% |
| Handwriting | 2 | 98.0% | 89.8% | — |

Shadows, background, and curved pages cause most errors; the adaptive
threshold handles much of that. Handwriting is not usable with Tesseract.

## Known limitations

- Accuracy is far from usable on real documents. Stylized fonts and stacked
  consonants are frequent failure points.
- Preprocessing can damage stacked characters and fine vowel marks. Test each
  transform on its own.
- Handwriting has not been benchmarked.
- PaddleOCR ([src/test_paddle.py](src/test_paddle.py)) currently fails with
  `No models are available for lang=bod`. No compatible Tibetan/Dzongkha
  recognition model has been found.
- `ocr.py` and `preprocessing.py` run on a hard-coded sample image when run directly.

## Data privacy

Do not upload agency or government documents to external services or AI tools
without explicit authorization. Keep corpus data on the local machine.
