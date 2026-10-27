"""
Preprocessing ablation: find which clean-up step helps or hurts OCR.

Runs each printed document with a reference transcript through a set of
preprocessing variants:
- original: no preprocessing
- each step on its own (upscale, grayscale, clahe, blur)
- full: all four steps (the default pipeline)
- full minus one step, for each step

Each run writes to a new timestamped folder in results/:
- results.csv: one row per image, variant, and language model
- raw/<image>__<lang>_<variant>.txt: the raw OCR output

Usage (from the project root):
    PYTHONPATH=src paddleocr_env/bin/python src/ablate_preprocessing.py
    PYTHONPATH=src paddleocr_env/bin/python src/ablate_preprocessing.py --langs dzo --psm 4
"""

import argparse
import csv
import time
from datetime import datetime

from jiwer import cer

from evaluate import CATEGORIES, RESULTS_DIR, find_labeled_images, normalize
from ocr import run_tesseract
from preprocessing import preprocess_image


STEPS = ["upscale", "grayscale", "clahe", "blur"]

# Variant name -> the steps switched on
VARIANTS = {"original": set()}
VARIANTS.update({f"only_{step}": {step} for step in STEPS})
VARIANTS["full"] = set(STEPS)
VARIANTS.update({f"full_minus_{step}": set(STEPS) - {step} for step in STEPS})

CSV_FIELDS = [
    "image", "lang", "psm", "variant", *STEPS,
    "cer", "ref_chars", "ocr_chars", "runtime_s",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--langs", nargs="+", default=["dzo", "bod"])
    parser.add_argument("--psm", type=int, default=6)
    args = parser.parse_args()

    run_dir = RESULTS_DIR / f"ablation_{datetime.now():%Y%m%d_%H%M%S}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True)

    # Only printed documents: handwriting and scene text fail regardless
    pairs = [
        (image_path, reference_path)
        for image_path, reference_path in find_labeled_images()
        if CATEGORIES.get(image_path.stem, "document") == "document"
    ]

    rows = []

    for image_path, reference_path in pairs:
        reference = normalize(reference_path.read_text(encoding="utf-8"))

        for lang in args.langs:
            for variant, steps in VARIANTS.items():
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

                print(f"{image_path.name:24} {lang:4} {variant:22} CER {rows[-1]['cer']:7.1%}")

    with open(run_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    # CER per variant: one column per image, then the mean
    images = [image_path.name for image_path, _ in pairs]
    short_names = [name.rsplit(".", 1)[0][:16] for name in images]

    for lang in args.langs:
        print(f"\nCER by variant, {lang}, PSM {args.psm}")
        print(f"  {'variant':22}" + "".join(f"{name:>18}" for name in short_names) + f"{'mean':>10}")

        for variant in VARIANTS:
            scores = [
                next(
                    row["cer"] for row in rows
                    if (row["image"], row["lang"], row["variant"]) == (image, lang, variant)
                )
                for image in images
            ]
            print(
                f"  {variant:22}"
                + "".join(f"{score:18.1%}" for score in scores)
                + f"{sum(scores) / len(scores):10.1%}"
            )

    print(f"\nSaved {len(rows)} rows to {run_dir}/")


if __name__ == "__main__":
    main()
