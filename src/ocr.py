import pytesseract
import cv2

from pathlib import Path

from preprocessing import preprocess_image


# Tesseract models kept in the repo (see models/README.md)
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def extract_text(image_path, lang="dzo", psm=6, preprocess=True):
    """
    Preprocess an image and extract Dzongkha text using Tesseract.

    lang is the Tesseract language model: "dzo" (Dzongkha), "bod" (Tibetan),
    "bod_uchen" (BDRC's Tibetan Uchen model), or a combination such as
    "dzo+bod".
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
    """
    Run Tesseract on an image array that is already prepared.

    Models in the project's models/ folder (such as bod_uchen) are used from
    there; others (dzo, bod) come from the system Tesseract install. A
    combination such as "dzo+bod" must come entirely from one place.
    """

    config = f"--psm {psm}"

    if all((MODELS_DIR / f"{part}.traineddata").exists() for part in lang.split("+")):
        config += f' --tessdata-dir "{MODELS_DIR}"'

    return pytesseract.image_to_string(
        image,
        lang=lang,
        config=config
    )


if __name__ == "__main__":
    image_path = "images/sample.jpeg"

    text = extract_text(image_path)

    print("Recognized Text:")
    print("----------------")
    print(text)