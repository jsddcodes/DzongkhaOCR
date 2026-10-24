import streamlit as st
import pytesseract
import tempfile
import os
from pathlib import Path

from ocr import extract_text
from preprocessing import preprocess_image


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_IMAGES = {
    "Printed character chart": PROJECT_ROOT / "test_data" / "printed_download.jpg",
    "Printed page": PROJECT_ROOT / "test_data" / "printed_text.jpeg",
}

LANGUAGE_MODELS = {
    "Dzongkha (dzo)": "dzo",
    "Tibetan (bod)": "bod",
}


# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Dzongkha OCR",
    page_icon="ཀ",
    layout="wide"
)


# -----------------------------
# Header
# -----------------------------

st.title("Dzongkha OCR")
st.write(
    "Extract Dzongkha text from a document image. "
    "This is an early prototype: expect frequent errors, "
    "especially with stacked characters and stylized fonts."
)

st.warning(
    "Demo only. Do not upload official, confidential, or personal documents.",
    icon=":material/warning:"
)


# -----------------------------
# Image source
# -----------------------------

source = st.segmented_control(
    "Image source",
    ["Sample image", "Upload your own"],
    default="Sample image"
)

image_path = None
temp_path = None

if source == "Upload your own":

    uploaded_file = st.file_uploader(
        "Upload a Dzongkha image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        # Save uploaded file temporarily so OpenCV can read it
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        image_path = temp_path

elif source == "Sample image":

    sample_name = st.selectbox("Sample", list(SAMPLE_IMAGES))
    image_path = str(SAMPLE_IMAGES[sample_name])


# -----------------------------
# Preview and OCR
# -----------------------------

if image_path is not None:

    try:
        processed_image = preprocess_image(image_path)
    except FileNotFoundError:
        processed_image = None
        st.error(
            "Could not read this image. Try a different PNG or JPEG file.",
            icon=":material/error:"
        )

    if processed_image is not None:

        left_column, right_column = st.columns(2)

        with left_column:

            st.subheader("Original image")
            st.image(image_path, width="stretch")

            st.subheader("Preprocessed image")
            st.image(
                processed_image,
                caption="2× upscaled, grayscale, contrast-enhanced, lightly blurred",
                width="stretch"
            )

        with right_column:

            st.subheader("Recognized text")

            language = st.segmented_control(
                "Language model",
                list(LANGUAGE_MODELS),
                default="Dzongkha (dzo)",
                help="Dzongkha and Tibetan share a script. "
                     "Either model may do better on a given image."
            )

            extract_button = st.button(
                "Extract text",
                type="primary",
                icon=":material/text_fields:",
                disabled=language is None
            )

            if extract_button:

                try:
                    with st.spinner("Processing image..."):
                        text = extract_text(
                            image_path,
                            lang=LANGUAGE_MODELS[language]
                        )
                except pytesseract.TesseractError as error:
                    st.error(f"OCR failed: {error}", icon=":material/error:")
                else:
                    st.text_area("OCR output", text, height=400)

                    st.download_button(
                        label="Download text",
                        data=text,
                        file_name="dzongkha_ocr.txt",
                        mime="text/plain",
                        icon=":material/download:"
                    )


# -----------------------------
# Clean up temporary file
# -----------------------------

if temp_path is not None and os.path.exists(temp_path):
    os.remove(temp_path)
