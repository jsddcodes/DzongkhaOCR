from pathlib import Path

from jiwer import cer

from ocr import extract_text


# Paths
IMAGE_PATH = Path("test_data/painting.jpeg")
GROUND_TRUTH_PATH = Path("ground_truth/painting.txt")


# Load ground truth
ground_truth = GROUND_TRUTH_PATH.read_text(encoding="utf-8")


# Run OCR using our existing pipeline
ocr_output = extract_text(str(IMAGE_PATH))


# Calculate Character Error Rate
error_rate = cer(ground_truth, ocr_output)
print("\nGround truth characters:", len(ground_truth))
print("OCR output characters:", len(ocr_output))


# Display results
print("\n" + "=" * 50)
print("Dzongkha OCR Evaluation")
print("=" * 50)

print("\nGround Truth:")
print(ground_truth)

print("\nOCR Output:")
print(ocr_output)

print("\nCharacter Error Rate (CER):")
print(f"{error_rate:.2%}")

print("=" * 50)