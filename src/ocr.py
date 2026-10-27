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
        image = preprocess_image(
            image_path,
            upscale=False,
            grayscale=False,
            crop_page=False,
            remove_shadows=False,
            clahe=False,
            blur=False,
            threshold=False,
            deskew=False,
        )

    return run_tesseract(image, lang=lang, psm=psm)


def run_tesseract(image, lang="dzo", psm=6):
    """Run Tesseract on an image array that is already prepared."""

    return pytesseract.image_to_string(
        image,
        lang=lang,
        config=f"--psm {psm}"
    )


if __name__ == "__main__":
    image_path = "images/sample.jpeg"

    text = extract_text(image_path)

    print("Recognized Text:")
    print("----------------")
    print(text)