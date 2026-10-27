import cv2
import numpy as np


def preprocess_image(
    image_path,
    upscale=False,
    grayscale=True,
    crop_page=False,
    remove_shadows=False,
    clahe=False,
    blur=True,
    threshold=True,
    deskew=False,
):
    """
    Prepare a Dzongkha image for OCR.

    The default is grayscale + blur + adaptive threshold. In the photo
    ablation (2026-10-27, 9 printed Dzongkha images) it cut mean CER from
    56.5% to 34.4% with bod, mainly by rescuing photos with shadows or
    background (75-96% -> 21-40%). It costs some accuracy on clean images
    (printed_download.jpg 17% -> 30%). CLAHE and upscaling hurt; crop and
    deskew did not help.

    Steps, in the order applied, each of which can be switched on or off:
    1. Upscale 2x
    2. Convert to grayscale
    3. Crop to the page (the largest bright region), for photos that
       show a table or background around the paper
    4. Remove shadows by dividing out a smoothed background estimate
    5. Improve contrast using CLAHE
    6. Apply light denoising
    7. Convert to black and white with an adaptive threshold
    8. Straighten tilted text

    Steps 3-5, 7 and 8 work on one channel, so they convert to grayscale
    even when grayscale=False. With every step off, the original image is
    returned in RGB order.
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
    if grayscale or crop_page or remove_shadows or clahe or threshold or deskew:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 3. Crop to the page
    if crop_page:
        image = _crop_to_page(image)

    # 4. Remove shadows
    if remove_shadows:
        image = _remove_shadows(image)

    # 5. Improve local contrast
    if clahe:
        image = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        ).apply(image)

    # 6. Light noise reduction
    if blur:
        image = cv2.GaussianBlur(
            image,
            (3, 3),
            0
        )

    # 7. Adaptive black and white
    if threshold:
        image = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15
        )

    # 8. Straighten tilted text
    if deskew:
        image = _deskew(image)

    # Colour images stay in OpenCV's BGR order until here
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image


def _crop_to_page(gray):
    """
    Crop to the largest bright region. Leaves the image unchanged when that
    region covers less than 30% of it (no clear page edge to find).
    """
    smoothed = cv2.GaussianBlur(gray, (25, 25), 0)
    otsu, _ = cv2.threshold(smoothed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 0.8 x Otsu keeps shadowed parts of the page; plain Otsu cut text off
    # the dim side of photographed pages
    _, mask = cv2.threshold(smoothed, 0.8 * otsu, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return gray

    page = max(contours, key=cv2.contourArea)

    if cv2.contourArea(page) < 0.3 * gray.shape[0] * gray.shape[1]:
        return gray

    x, y, w, h = cv2.boundingRect(page)
    return gray[y:y + h, x:x + w]


def _remove_shadows(gray):
    """
    Estimate the background (paper and shadows) by removing the text with
    a dilation and a median blur, then divide it out so the paper becomes
    evenly white.
    """
    background = cv2.medianBlur(
        cv2.dilate(gray, np.ones((7, 7), np.uint8)),
        21
    )
    return cv2.divide(gray, background, scale=255)


def _deskew(gray):
    """
    Rotate so text lines are horizontal. The angle comes from the minimum
    area rectangle around the dark (text) pixels. Angles beyond 15 degrees
    are ignored as unreliable.
    """
    _, ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    points = cv2.findNonZero(ink)

    if points is None:
        return gray

    angle = cv2.minAreaRect(points)[-1]

    # minAreaRect reports angles in (0, 90]; map to the nearest tilt
    if angle > 45:
        angle -= 90

    if abs(angle) < 0.1 or abs(angle) > 15:
        return gray

    h, w = gray.shape
    rotation = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(
        gray,
        rotation,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


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
