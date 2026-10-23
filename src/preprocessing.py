import cv2


def preprocess_image(image_path):
    """
    Prepare a Dzongkha image for OCR.

    Steps:
    1. Read the image
    2. Upscale 2x
    3. Convert to grayscale
    4. Improve contrast using CLAHE
    5. Apply light denoising
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not open image: {image_path}")

    # 1. Upscale the image
    upscaled = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # 2. Convert to grayscale
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

    # 3. Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # 4. Light noise reduction
    denoised = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0
    )

    return denoised


if __name__ == "__main__":
    image_path = "images/sample.jpeg"

    processed = preprocess_image(image_path)

    cv2.imwrite(
        "results/preprocessed.png",
        processed
    )

    print(
        "Preprocessed image saved to "
        "results/preprocessed.png"
    )