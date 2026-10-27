"""
Error analysis: which kinds of characters does the OCR get wrong?

Aligns each OCR output with its reference transcript (exact Levenshtein
edit operations, after the same normalization as evaluate.py) and sorts
every error by the character involved:

- consonant: base letters (ཀ–ཨ)
- stacked: subjoined letters written below another (ྐ–ྼ)
- vowel/mark: vowel signs and other marks (ི ུ ེ ོ ཱ ཾ ...)
- tsheg: the syllable dot (་)
- shad: sentence and verse marks (། ༎ ...)
- space
- digit: Tibetan or ASCII digits
- other: anything else, mostly Latin letters or symbols from noise

Each error is a missed character (in the reference, not in the output),
an extra character (in the output only), or a substitution (one replaced
by another; counted under the reference character's type).

Usage (from the project root):
    PYTHONPATH=src paddleocr_env/bin/python src/error_analysis.py
    PYTHONPATH=src paddleocr_env/bin/python src/error_analysis.py --lang bod --no-preprocess
"""

import argparse
from collections import Counter

from rapidfuzz.distance import Levenshtein

from evaluate import CATEGORIES, DOCUMENT_CATEGORIES, find_labeled_images, normalize
from ocr import extract_text


TYPES = ["consonant", "stacked", "vowel/mark", "tsheg", "shad", "space", "digit", "other"]
KINDS = ["missed", "extra", "substituted"]


def char_type(char):
    code = ord(char)

    if char == " ":
        return "space"
    if char == "་":
        return "tsheg"
    if 0x0F0D <= code <= 0x0F14:
        return "shad"
    if 0x0F20 <= code <= 0x0F29 or char.isdigit():
        return "digit"
    if 0x0F40 <= code <= 0x0F6C:
        return "consonant"
    if 0x0F90 <= code <= 0x0FBC:
        return "stacked"
    if 0x0F71 <= code <= 0x0F87:
        return "vowel/mark"
    return "other"


def count_errors(reference, output):
    """Count errors by (kind, character type)."""
    counts = Counter()

    for op in Levenshtein.editops(reference, output):
        if op.tag == "delete":
            counts["missed", char_type(reference[op.src_pos])] += 1
        elif op.tag == "insert":
            counts["extra", char_type(output[op.dest_pos])] += 1
        else:
            counts["substituted", char_type(reference[op.src_pos])] += 1

    return counts


def print_table(title, counts, reference_chars):
    total = sum(counts.values())
    print(f"\n{title}: {total} errors over {reference_chars} reference characters")
    print(f"  {'type':12}" + "".join(f"{kind:>13}" for kind in KINDS) + f"{'total':>9}{'share':>8}")

    for char_type_name in TYPES:
        row = [counts[kind, char_type_name] for kind in KINDS]

        if sum(row):
            print(
                f"  {char_type_name:12}" + "".join(f"{n:13}" for n in row)
                + f"{sum(row):9}{sum(row) / total:8.0%}"
            )

    print(f"  {'all':12}" + "".join(
        f"{sum(counts[kind, t] for t in TYPES):13}" for kind in KINDS
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--lang", default="bod_uchen")
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--no-preprocess", action="store_true")
    args = parser.parse_args()

    totals = {}

    for image_path, reference_path in find_labeled_images():
        category = CATEGORIES.get(image_path.stem, "dzongkha")

        if category not in DOCUMENT_CATEGORIES:
            continue

        reference = normalize(reference_path.read_text(encoding="utf-8"))
        output = normalize(extract_text(
            str(image_path), lang=args.lang, psm=args.psm,
            preprocess=not args.no_preprocess
        ))
        counts = count_errors(reference, output)

        missed, extra, substituted = (sum(counts[k, t] for t in TYPES) for k in KINDS)
        print(
            f"{image_path.name:24} {category:9} missed {missed:4}  extra {extra:4}  "
            f"substituted {substituted:4}  (reference {len(reference)} chars)"
        )

        category_counts, category_chars = totals.get(category, (Counter(), 0))
        totals[category] = (category_counts + counts, category_chars + len(reference))

    for category, (counts, reference_chars) in sorted(totals.items()):
        print_table(f"{category}, {args.lang}", counts, reference_chars)


if __name__ == "__main__":
    main()
