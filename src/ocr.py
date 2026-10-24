import pytesseract
import cv2

from preprocessing import preprocess_image


def extract_text(image_path, lang="dzo"):
    """
    Preprocess an image and extract Dzongkha text using Tesseract.

    lang is the Tesseract language model: "dzo" (Dzongkha) or "bod" (Tibetan).
    """

    # Preprocess the image
    processed_image = preprocess_image(image_path)

    # Run Tesseract with the chosen language model
    text = pytesseract.image_to_string(
        processed_image,
        lang=lang,
        config="--psm 6"
    )

    return text


if __name__ == "__main__":
    image_path = "images/sample.jpeg"

    text = extract_text(image_path)

    print("Recognized Text:")
    print("----------------")
    print(text)