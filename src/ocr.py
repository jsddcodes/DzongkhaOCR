import pytesseract
import cv2

from preprocessing import preprocess_image


def extract_text(image_path, lang="dzo", psm=6, preprocess=True):
    """
    Preprocess an image and extract Dzongkha text using Tesseract.

    lang is the Tesseract language model: "dzo" (Dzongkha), "bod" (Tibetan),
    or a combination such as "dzo+bod".
    psm is Tesseract's page segmentation mode.
    preprocess=False runs Tesseract on the original image.
    """

    if preprocess:
        image = preprocess_image(image_path)
    else:
        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(f"Could not open image: {image_path}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run Tesseract with the chosen language model
    text = pytesseract.image_to_string(
        image,
        lang=lang,
        config=f"--psm {psm}"
    )

    return text


if __name__ == "__main__":
    image_path = "images/sample.jpeg"

    text = extract_text(image_path)

    print("Recognized Text:")
    print("----------------")
    print(text)