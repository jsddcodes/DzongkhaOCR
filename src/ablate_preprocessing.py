"""
Preprocessing ablation: find which clean-up steps help or hurt OCR.

Runs each printed document with a reference transcript through a set of
preprocessing variants. Two groups:
- base: the original four steps (upscale, grayscale, clahe, blur): the
  original image, each step on its own, all four, and all four minus each
- photo: steps for real photos (crop to page, shadow removal, adaptive
  threshold, deskew) added on top of grayscale + blur. The current
  pipeline default is "gray_blur+threshold"

Each run writes to a new timestamped folder in results/:
- results.csv: one row per image, variant, and language model
- raw/<image>__<lang>_<variant>.txt: the raw OCR output

Usage (from the project root):
    PYTHONPATH=src paddleocr_env/bin/python src/ablate_preprocessing.py
    PYTHONPATH=src paddleocr_env/bin/python src/ablate_preprocessing.py --group photo --langs bod
"""

import argparse
import csv
import time
from datetime import datetime

from jiwer import cer

from evaluate import (
    CATEGORIES, DOCUMENT_CATEGORIES, RESULTS_DIR, find_labeled_images, normalize
)
from ocr import run_tesseract
from preprocessing import preprocess_image


BASE_STEPS = ["upscale", "grayscale", "clahe", "blur"]
PHOTO_STEPS = ["crop_page", "remove_shadows", "threshold", "deskew"]
STEPS = BASE_STEPS + PHOTO_STEPS

GRAY_BLUR = {"grayscale", "blur"}

# Variant name -> the steps switched on
BASE_VARIANTS = {"original": set()}
BASE_VARIANTS.update({f"only_{step}": {step} for step in BASE_STEPS})
BASE_VARIANTS["base_full"] = set(BASE_STEPS)
BASE_VARIANTS.update({f"base_full_minus_{step}": set(BASE_STEPS) - {step} for step in BASE_STEPS})

PHOTO_VARIANTS = {
    "gray_blur": GRAY_BLUR,
    "gray_blur+crop": GRAY_BLUR | {"crop_page"},
    "gray_blur+shadows": GRAY_BLUR | {"remove_shadows"},
    "gray_blur+threshold": GRAY_BLUR | {"threshold"},
    "gray_blur+deskew": GRAY_BLUR | {"deskew"},
    "gray_blur+shadows+threshold": GRAY_BLUR | {"remove_shadows", "threshold"},
    "gray_blur+crop+shadows": GRAY_BLUR | {"crop_page", "remove_shadows"},
    "gray_blur+crop+shadows+threshold": GRAY_BLUR | {"crop_page", "remove_shadows", "threshold"},
    "all_photo_steps": GRAY_BLUR | set(PHOTO_STEPS),
}

GROUPS = {
    "base": BASE_VARIANTS,
    "photo": PHOTO_VARIANTS,
    "all": {**BASE_VARIANTS, **PHOTO_VARIANTS},
}

CSV_FIELDS = [
    "image", "category", "lang", "psm", "variant", *STEPS,
    "cer", "ref_chars", "ocr_chars", "runtime_s",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--langs", nargs="+", default=["dzo", "bod", "bod_uchen"])
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--group", choices=GROUPS, default="all")
    args = parser.parse_args()

    variants = GROUPS[args.group]

    run_dir = RESULTS_DIR / f"ablation_{datetime.now():%Y%m%d_%H%M%S}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True)

    # Only printed documents: handwriting and scene text fail regardless
    pairs = [
        (image_path, reference_path, CATEGORIES.get(image_path.stem, "dzongkha"))
        for image_path, reference_path in find_labeled_images()
        if CATEGORIES.get(image_path.stem, "dzongkha") in DOCUMENT_CATEGORIES
    ]

    rows = []

    for image_path, reference_path, category in pairs:
        reference = normalize(reference_path.read_text(encoding="utf-8"))

        for lang in args.langs:
            for variant, steps in variants.items():
                start = time.perf_counter()
                image = preprocess_image(
                    str(image_path), **{step: step in steps for step in STEPS}
                )
                raw_output = run_tesseract(image, lang=lang, psm=args.psm)
                runtime = time.perf_counter() - start

                (raw_dir / f"{image_path.stem}__{lang}_{variant}.txt").write_text(
                    raw_output, encoding="utf-8"
                )

                output = normalize(raw_output)

                rows.append({
                    "image": image_path.name,
                    "category": category,
                    "lang": lang,
                    "psm": args.psm,
                    "variant": variant,
                    **{step: step in steps for step in STEPS},
                    # jiwer requires a non-empty hypothesis; empty output = 100% error
                    "cer": round(cer(reference, output), 4) if output else 1.0,
                    "ref_chars": len(reference),
                    "ocr_chars": len(output),
                    "runtime_s": round(runtime, 2),
                })

                print(f"{image_path.name:24} {lang:4} {variant:32} CER {rows[-1]['cer']:7.1%}")

    with open(run_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    # Mean CER per variant, one column per category and language model.
    # Per-image scores are in results.csv.
    categories = sorted({category for _, _, category in pairs})
    columns = [(category, lang) for category in categories for lang in args.langs]

    print(f"\nMean CER by variant, PSM {args.psm}")
    print(f"  {'variant':32}" + "".join(
        f"{f'{category} {lang}':>16}" for category, lang in columns
    ))

    for variant in variants:
        means = []

        for category, lang in columns:
            scores = [
                row["cer"] for row in rows
                if (row["category"], row["lang"], row["variant"]) == (category, lang, variant)
            ]
            means.append(sum(scores) / len(scores))

        print(f"  {variant:32}" + "".join(f"{mean:16.1%}" for mean in means))

    counts = ", ".join(
        f"{category}: {sum(1 for _, _, c in pairs if c == category)}" for category in categories
    )
    print(f"\nImages per category: {counts}")
    print(f"Saved {len(rows)} rows to {run_dir}/")


if __name__ == "__main__":
    main()
