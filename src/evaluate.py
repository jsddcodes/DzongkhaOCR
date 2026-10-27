"""
Batch evaluation: score every image that has a reference transcript
across a grid of OCR configurations.

Each run writes to a new timestamped folder in results/:
- results.csv: one row per image and configuration
- raw/<image>__<config>.txt: the raw OCR output, before normalization

Usage (from the project root):
    PYTHONPATH=src paddleocr_env/bin/python src/evaluate.py
    PYTHONPATH=src paddleocr_env/bin/python src/evaluate.py --langs bod --psms 6
"""

import argparse
import csv
import itertools
import re
import time
import unicodedata
from datetime import datetime
from pathlib import Path

from jiwer import cer, wer

from ocr import extract_text


GROUND_TRUTH_DIR = Path("ground_truth")
IMAGE_DIR = Path("test_data")
RESULTS_DIR = Path("results")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Each image is scored in one category. Printed documents are split by
# language: Dzongkha, and Classical Tibetan (Chöke) used for Buddhist texts.
# Anything not listed here counts as "dzongkha".
CATEGORIES = {
    "prayer": "tibetan",
    "painting": "scene",
    "written_image": "handwriting",
    "handwriting": "handwriting",
    "low_quality_handwriting": "handwriting",
}

DOCUMENT_CATEGORIES = {"dzongkha", "tibetan"}

CSV_FIELDS = [
    "image", "category", "lang", "psm", "preprocess",
    "cer", "cer_nospace", "wer", "exact_match", "ref_chars", "ocr_chars", "runtime_s",
]


def normalize(text):
    """
    Normalize text before scoring: Unicode NFC, collapse runs of
    whitespace (including newlines) to one space, trim the ends.
    Tsheg and shad are left as they are.
    """
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def cer_without_spaces(reference, output):
    """CER after removing every space from both normalized texts."""
    reference, output = reference.replace(" ", ""), output.replace(" ", "")
    return round(cer(reference, output), 4) if output else 1.0


def find_labeled_images():
    """Pair each ground_truth/<stem>.txt with test_data/<stem>.<ext>."""
    pairs = []

    for reference_path in sorted(GROUND_TRUTH_DIR.glob("*.txt")):
        matches = [
            path for path in IMAGE_DIR.glob(f"{reference_path.stem}.*")
            if path.suffix.lower() in IMAGE_EXTENSIONS
        ]

        if not matches:
            print(f"Skipping {reference_path}: no matching image in {IMAGE_DIR}/")
            continue

        pairs.append((matches[0], reference_path))

    return pairs


def config_name(lang, psm, preprocess):
    return f"{lang}_psm{psm}_{'pre' if preprocess else 'orig'}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--langs", nargs="+", default=["dzo", "bod", "dzo+bod", "bod_uchen"])
    parser.add_argument("--psms", nargs="+", type=int, default=[4, 6])
    args = parser.parse_args()

    run_dir = RESULTS_DIR / f"eval_{datetime.now():%Y%m%d_%H%M%S}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True)

    rows = []
    configs = list(itertools.product(args.langs, args.psms, [True, False]))

    for image_path, reference_path in find_labeled_images():
        reference = normalize(reference_path.read_text(encoding="utf-8"))

        if not reference:
            print(f"Skipping {reference_path}: empty reference")
            continue

        category = CATEGORIES.get(image_path.stem, "dzongkha")

        for lang, psm, preprocess in configs:
            name = config_name(lang, psm, preprocess)

            start = time.perf_counter()
            raw_output = extract_text(
                str(image_path), lang=lang, psm=psm, preprocess=preprocess
            )
            runtime = time.perf_counter() - start

            (raw_dir / f"{image_path.stem}__{name}.txt").write_text(
                raw_output, encoding="utf-8"
            )

            output = normalize(raw_output)

            rows.append({
                "image": image_path.name,
                "category": category,
                "lang": lang,
                "psm": psm,
                "preprocess": preprocess,
                # jiwer requires a non-empty hypothesis; empty output = 100% error
                "cer": round(cer(reference, output), 4) if output else 1.0,
                # Secondary: CER with all spaces removed. Spacing between
                # Dzongkha phrases varies with typesetting, so this isolates
                # errors in the letters and punctuation themselves
                "cer_nospace": cer_without_spaces(reference, output),
                # Split on spaces only; Dzongkha marks syllables with tsheg,
                # so this is a rough phrase-level measure
                "wer": round(wer(reference, output), 4) if output else 1.0,
                "exact_match": output == reference,
                "ref_chars": len(reference),
                "ocr_chars": len(output),
                "runtime_s": round(runtime, 2),
            })

            print(f"{image_path.name:28} {name:22} CER {rows[-1]['cer']:7.1%}")

    with open(run_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    # Mean CER per configuration, kept separate by category
    print("\nMean CER by category and configuration")
    print("=" * 50)

    for category in sorted({row["category"] for row in rows}):
        category_rows = [row for row in rows if row["category"] == category]
        images = len({row["image"] for row in category_rows})
        print(f"\n{category} ({images} image{'s' if images != 1 else ''})")

        for lang, psm, preprocess in configs:
            scores = [
                row["cer"] for row in category_rows
                if (row["lang"], row["psm"], row["preprocess"]) == (lang, psm, preprocess)
            ]
            nospace = [
                row["cer_nospace"] for row in category_rows
                if (row["lang"], row["psm"], row["preprocess"]) == (lang, psm, preprocess)
            ]
            print(
                f"  {config_name(lang, psm, preprocess):22} {sum(scores) / len(scores):7.1%}"
                f"   (ignoring spaces {sum(nospace) / len(nospace):6.1%})"
            )

    print(f"\nSaved {len(rows)} rows to {run_dir}/")


if __name__ == "__main__":
    main()
