import cv2


def preprocess_image(image_path, upscale=False, grayscale=True, clahe=False, blur=True):
    """
    Prepare a Dzongkha image for OCR.

    The default is grayscale + blur. In the preprocessing ablation
    (2026-10-27, 3 printed images) it had the lowest mean CER; CLAHE
    roughly doubled errors on photographed pages, and upscaling hurt
    when combined with blur.

    Steps, each of which can be switched on or off:
    1. Upscale 2x
    2. Convert to grayscale
    3. Improve contrast using CLAHE (works on one channel, so it
       converts to grayscale even when grayscale=False)
    4. Apply light denoising

    With every step off, the original image is returned in RGB order.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not open image: {image_path}")

    # 1. Upscale the image
    if upscale:
        image = cv2.resize(
            image,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

    # 2. Convert to grayscale
    if grayscale or clahe:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. Improve local contrast
    if clahe:
        image = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        ).apply(image)

    # 4. Light noise reduction
    if blur:
        image = cv2.GaussianBlur(
            image,
            (3, 3),
            0
        )

    # Colour images stay in OpenCV's BGR order until here
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image


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