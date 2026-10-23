# Dzongkha OCR Project --- Technical Handoff

**Owner:** Jigme Dorji\
**Project directory:** `DzongkhaOCR`\
**Updated:** 22 October 2026\
**Purpose:** Transfer technical context, prior experiments, known
failures, and next actions to another AI assistant or developer.

> **Accuracy note:** This document is based on earlier project
> conversations and code snippets. The current repository was not
> inspected while creating this handoff. Verify current files, package
> versions, model availability, and implementation status before making
> changes.

## 1. Goal and intended outcome

Build a working prototype that recognizes Dzongkha text from document
images, potentially supporting Bhutanese public-service digitization.

The prototype should accept an image, optionally preprocess it, run OCR
with a suitable Dzongkha/Tibetan configuration, display extracted text,
and be evaluated against human-checked ground-truth transcriptions. The
immediate priority is a reproducible baseline and honest
evaluation---not a claim of production readiness.

Handwriting has been tested, but whether it is a required first-release
feature remains to be confirmed. Other useful test categories include
printed text, scanned pages, older/noisy documents, and multiple fonts.

## 2. Current status summary

  ------------------------------------------------------------------------
  Area                    Last reported state     What to verify
  ----------------------- ----------------------- ------------------------
  Computer                MacBook Pro with Apple  Exact macOS version
                          M4 Pro                  

  Python                  Python 3.11.x; 3.11.15  Active
                          recorded once           interpreter/version

  Tesseract               Installed and used for  Binary path, version,
                          experiments             language packs

  `pytesseract`           0.3.13 recorded         Active environment
                                                  version

  OpenCV                  `opencv-python`         Confirm actual version
                          5.0.0.93 recorded       

  PaddleOCR stack         PaddleOCR 3.7.0,        Installed versions and
                          PaddlePaddle 3.3.1,     current model support
                          PaddleX 3.7.2 recorded  

  Streamlit               Planned for the         Check whether app is
                          prototype UI            implemented and runs

  Preprocessing           OpenCV image loading,   Inspect
                          2× upscaling, grayscale `src/preprocessing.py`
                          explored                

  Ground truth            A `ground_truth/`       Verify actual verified
                          directory was mentioned transcripts

  Agency corpus           Agency may be able to   Availability, format,
                          provide a Dzongkha      permissions not
                          corpus                  confirmed

  Handwriting results     Rough results reported: Metric and sample count
                          `bod` \~20%, `dzo`      undocumented
                          \~10%                   
  ------------------------------------------------------------------------

These are historical notes, not a verified snapshot of the current
codebase.

## 3. Setup and environment

### Hardware and OS

-   MacBook Pro with Apple M4 Pro chip.
-   macOS; exact version was not captured in the available notes.
-   Earlier shell prompt resembled
    `jigmesingyedorji@Jigmes-MacBook-Pro-8`.
-   Project folder: `DzongkhaOCR`.
-   A virtual environment named `paddleocr_env` was used for PaddleOCR
    experiments.

### Previously recorded package versions

  Tool/library       Recorded version or detail
  ------------------ ------------------------------------------------------
  Python             3.11.15 in one note; otherwise Python 3.11.x
  `pytesseract`      0.3.13
  `paddleocr`        3.7.0
  `paddlepaddle`     3.3.1
  `paddlex`          3.7.2
  `opencv-python`    5.0.0.93 was recorded; verify
  Pillow             Used; version not recorded
  Streamlit          Planned/used in project design; version not recorded
  Tesseract binary   Installed; exact version/path not recorded

### Initial diagnostic commands

Run from the project directory and activate the intended virtual
environment first:

``` bash
pwd
find . -maxdepth 3 -type f | sort
git status --short
python --version
which python
python -m pip list
which tesseract
tesseract --version
tesseract --list-langs
```

Check Python packages where installed:

``` bash
python -c "import pytesseract; print(pytesseract.__version__)"
python -c "import cv2; print(cv2.__version__)"
python -c "import PIL; print(PIL.__version__)"
python -c "import streamlit; print(streamlit.__version__)"
```

Do not assume `paddleocr_env` is also the correct environment for
Tesseract and Streamlit. If dependencies conflict, use a separate
baseline environment and record setup steps.

## 4. Tools and roles

### Tesseract + `pytesseract`

Tesseract is the current practical baseline candidate because earlier
checks indicated that relevant language data, including `bod` and `dzo`,
was installed. `pytesseract` calls the local Tesseract executable from
Python.

An installed language pack does not guarantee good accuracy. Compare
relevant configurations on the same ground-truthed images.

### OpenCV (`cv2`)

Used for image loading and preprocessing. Candidate experiments include
original image, upscaling, grayscale, thresholding, denoising,
deskewing, and contrast adjustment. Test each independently: aggressive
processing can damage Dzongkha's stacked characters and fine marks.

### Pillow

Useful for image handling and potentially Streamlit upload workflows.
Exact usage/version needs verification.

### Streamlit

Intended for a simple demo UI: upload image, preview it, run OCR, and
display output. Do not assume `src/streamlit_app.py` is complete until
inspected and run.

### PaddleOCR / PaddlePaddle / PaddleX

Explored as an alternative. The recorded stack was PaddleOCR 3.7.0,
PaddlePaddle 3.3.1, and PaddleX 3.7.2. The attempted Dzongkha/Tibetan
language configuration failed because no matching model was available in
that configuration.

## 5. Last known project structure

The previously described structure was:

``` text
DzongkhaOCR/
├── images/
├── results/
├── ground_truth/
└── src/
    ├── test_paddle.py
    ├── preprocessing.py
    ├── ocr.py
    └── streamlit_app.py
```

This is the last known intended layout, not a verified current listing.

-   `images/`: test input images.
-   `ground_truth/`: reference transcriptions mapped to image IDs.
-   `results/`: predictions, logs, and evaluation output.
-   `src/preprocessing.py`: image loading/preprocessing.
-   `src/ocr.py`: OCR engine wrapper.
-   `src/streamlit_app.py`: user-facing prototype.
-   `src/test_paddle.py`: experimental PaddleOCR test.

Inspect the actual repository and preserve existing work before editing.

## 6. Key preprocessing code shared previously

``` python
import cv2


def preprocess_image(image_path):
    """
    Prepare a Dzongkha image for OCR.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not open image: {image_path}")

    # Upscale the image to give Tesseract more pixels to work with
    upscaled = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert to grayscale
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

    # Additional preprocessing can be evaluated here.
    return gray
```

### What it does

1.  Reads an image from a filesystem path.
2.  Raises an error if OpenCV cannot open it.
3.  Resizes it to twice the width and height using cubic interpolation.
4.  Converts it to grayscale.
5.  Returns the grayscale image array.

### Limitations

-   Accepts a filesystem path, not a Streamlit `UploadedFile` directly.
-   Always upscales and converts to grayscale; compare with the
    original.
-   Does not deskew, denoise, threshold, or save intermediate output.
-   It has not been established that these transformations improve OCR
    accuracy.

This is a previously shared snippet, not necessarily the current file.
Inspect `src/preprocessing.py` before replacing it.

## 7. Minimal Tesseract diagnostic snippet

This is a suggested baseline test, not a claim that the exact code
already exists in `src/ocr.py`:

``` python
import pytesseract
from preprocessing import preprocess_image


def run_tesseract(image_path: str, lang: str = "dzo") -> str:
    image = preprocess_image(image_path)
    return pytesseract.image_to_string(image, lang=lang)
```

Depending on how scripts are run, the import may need to be
`from src.preprocessing import preprocess_image`. Resolve imports
consistently.

Command-line checks:

``` bash
tesseract path/to/image.png stdout -l dzo
tesseract path/to/image.png stdout -l bod
```

If Python cannot find the Tesseract binary, check `which tesseract`
before setting `pytesseract.pytesseract.tesseract_cmd`.

For each experiment, save image ID, engine/version, language
configuration, preprocessing variant, raw output, runtime, and metrics
if ground truth is available. Keep raw outputs rather than overwriting
them.

## 8. What has worked

Based on earlier conversations:

1.  **Tesseract was available locally.** Language data including `bod`
    and `dzo` was reported. Reconfirm with `tesseract --list-langs`.
2.  **OpenCV preprocessing was explored.** The shared code provides a
    path-based loading, 2× resize, and grayscale baseline.
3.  **PaddleOCR was installed in a separate environment.** It was
    possible to import the package and inspect the constructor
    signature.
4.  **PaddleOCR's 3.x interface was inspected.** Options included
    document orientation classification, unwarping, text detection, and
    recognition model configuration; exact API details depend on
    version.
5.  **A project structure was planned.** `images/`, `results/`,
    `ground_truth/`, and `src/` were described.
6.  **Handwriting was tested preliminarily.** Approximate results were
    reported as `bod` 20% and `dzo` 10%, but scoring method and sample
    count were not documented.

"Worked" means reported as available or tried, not independently
verified during this handoff.

## 9. What failed and why

### A. PaddleOCR could not resolve the requested `bod` model

Recorded error:

``` text
ValueError: No models are available for lang=bod and ocr_version=None
```

**Likely cause:** The installed PaddleOCR/PaddleX configuration did not
have a model corresponding to that requested language setting. This is a
model/configuration availability issue, not necessarily an
image-processing issue.

**Recommended response:** 1. Confirm installed versions. 2. Check
current PaddleOCR documentation and model lists for an actual compatible
recognition model. 3. If no suitable model exists, do not keep guessing
language parameters. 4. Continue with Tesseract as the baseline;
investigate custom training only if data, compute, time, and permissions
make it feasible.

### B. Input filename mismatch

A prior test expected `Image1.jpg`, while the actual file was
`Image1.png`.

**Cause:** The expected path/extension did not match the actual file, so
the test could not load the intended image. This is not an OCR accuracy
failure.

Use:

``` bash
find images -type f
```

Then use the exact filename and extension.

### C. Poor preliminary handwriting recognition

Reported approximate performance was 20% for `bod` and 10% for `dzo`.

**Caveat:** The metric, test-set size, and evaluation method were not
recorded. Do not treat these figures as formal benchmark results.

**Possible contributing factors:** handwritten script differs from
printed training data; language model mismatch; low resolution or image
noise; stacked-character complexity; insufficient task-specific training
data. These are hypotheses to test, not confirmed diagnoses.

### D. Preprocessing may not be enough

Upscaling and grayscale conversion cannot compensate for an unsuitable
OCR model or inadequate training data. Evaluate transformations
quantitatively instead of assuming they help.

## 10. Current problems and unknowns

1.  Current repository state is unknown in this handoff. Inspect actual
    files, imports, dependencies, and working tree.
2.  No verified benchmark is documented. Handwriting percentages lack a
    stated metric and sample count.
3.  Best Tesseract configuration is undetermined. Compare `dzo` and
    `bod` on the same labeled set.
4.  PaddleOCR model availability is unresolved. The previous
    configuration failed; verify support before further work.
5.  Ground-truth readiness is unknown. A folder was mentioned, but
    number and quality of transcripts are not known.
6.  Agency corpus is not confirmed received. Format, size,
    image/transcription alignment, and restrictions need clarification.
7.  Streamlit status is unknown. It was part of the planned
    architecture; verify whether it runs end to end.
8.  Deadline and required document types need confirmation. An earlier
    target around the 20th of the following month was mentioned, but the
    exact month and current deliverables are uncertain.
9.  Data privacy matters. Do not upload confidential government
    documents to external AI services or public OCR services unless the
    agency explicitly authorizes it.

## 11. Evaluation plan

Create a small representative test set and human-verify each reference
transcription. Possible categories: - Clean printed Dzongkha. - Scanned
pages. - Older/noisy or low-contrast documents. - Multiple fonts. -
Handwriting, if required and samples are available.

Keep development samples separate from a final held-out test set if
model training is introduced.

### Recommended metrics

-   **Character Error Rate (CER):**
    `(substitutions + deletions + insertions) / number of reference characters`.
-   **Word Error Rate (WER):** useful if tokenization and spacing are
    consistent enough.
-   **Exact-match rate:** fraction of complete samples that match the
    reference exactly.
-   **Runtime:** practical processing time per image/page.

Define Unicode normalization, whitespace, punctuation, and tokenization
rules before comparing outputs. Preserve raw output as well as
normalized text. Dzongkha Unicode representation and spacing conventions
can affect metrics.

Inspect errors such as stacked characters, similar-looking glyphs,
spacing, punctuation/numerals, blur, skew, noise, fonts, handwriting,
and text segmentation. Compare engines/configurations on identical
images.

## 12. Agency corpus: questions to resolve

The owner reported that the agency may provide a Dzongkha corpus if
needed. Availability has not been confirmed.

Clarify: - Is it images, scanned PDFs, plain text, paired images and
transcripts, or mixed data? - Does it contain printed text, handwriting,
or both? - Are transcriptions human-verified and aligned with individual
images/pages? - How large and diverse is it? - Is it authorized for this
internship and for model training? - Are there confidentiality,
retention, access, or deletion rules? - May data be sent to external AI
tools, or must it stay local? - May trained model weights or sample
outputs be shared?

A text-only corpus may help with language resources, but supervised
visual OCR training generally benefits from image/transcription pairs.
Do not upload sensitive government data to Claude, ChatGPT, or external
services without explicit authorization.

## 13. Recommended next steps, in order

1.  **Inspect the live repository.** Read existing files and run
    `git status --short`; do not overwrite working code.
2.  **Verify the active environment.** Record Python, Tesseract, OpenCV,
    `pytesseract`, Streamlit, and PaddleOCR versions.
3.  **Run one image end to end.** Confirm image path, preprocessing,
    Tesseract invocation, and Dzongkha Unicode output.
4.  **Resolve language settings.** Run the same image with `dzo` and
    `bod`, and save raw outputs.
5.  **Build a small labeled benchmark.** Use human-checked transcripts
    and document normalization rules.
6.  **Compare preprocessing variants.** Original image
    vs. grayscale/upscaled image; then test other transforms one at a
    time.
7.  **Calculate CER and inspect errors.** Avoid informal accuracy
    estimates where repeatable metrics are possible.
8.  **Finish the minimal Streamlit workflow.** Upload, preview, run OCR,
    display output, and handle invalid files.
9.  **Check corpus availability and restrictions.** Decide whether model
    training is feasible within the deadline.
10. **Write the technical report.** Include pipeline, dataset, metrics,
    failure examples, limitations, and next-phase recommendations.

If model training is not realistic within the available time, a
well-documented baseline and honest evaluation are stronger than an
unvalidated custom model.

## 14. Experiment log template

Use one entry per experiment:

-   **Date / experiment ID:**
-   **Question being tested:**
-   **Image IDs / sample count:**
-   **Engine and version:**
-   **Language/model configuration:**
-   **Preprocessing variant:**
-   **Normalization rules:**
-   **CER / WER / exact-match / runtime:**
-   **Failure patterns:**
-   **Conclusion:**
-   **Next action:**

## 15. Prompt for the next assistant

> Continue my Dzongkha OCR project in the `DzongkhaOCR` repository.
> First inspect the actual repository and environment; do not assume
> this handoff reflects current files. The project aims to recognize
> Dzongkha from document images. Tesseract via `pytesseract` is the
> practical baseline candidate, with OpenCV preprocessing and a planned
> Streamlit interface. Previous notes recorded Python 3.11.x,
> `pytesseract` 0.3.13, OpenCV 5.0.0.93, PaddleOCR 3.7.0, PaddlePaddle
> 3.3.1, and PaddleX 3.7.2, but verify all versions. PaddleOCR
> previously failed with
> `ValueError: No models are available for lang=bod and ocr_version=None`.
> A test also failed due to expecting `Image1.jpg` when the file was
> `Image1.png`. Preliminary handwriting results were reported as `bod`
> 20% and `dzo` 10%, but metric and sample count are unknown. The agency
> may provide a Dzongkha corpus, not yet confirmed received. Start by
> getting one known image through the existing pipeline, compare `dzo`
> and `bod`, create a ground-truthed benchmark, and measure CER.
> Preserve existing code, make small testable changes, and report exact
> commands and results. Do not upload confidential corpus data to
> external tools without authorization.

------------------------------------------------------------------------

**Handoff status:** This file is a technical context transfer based on
prior conversations, not a verified repository snapshot. Confirm
implementation status, environment versions, dataset availability,
performance, and deadline before relying on them.
