import streamlit as st
import tempfile
import os

from ocr import extract_text
from preprocessing import preprocess_image


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
    "Upload a Dzongkha document or image to extract its text."
)


# -----------------------------
# File upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload a Dzongkha image",
    type=["png", "jpg", "jpeg"]
)


if uploaded_file is not None:

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(uploaded_file.name)[1]
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name


    # -----------------------------
    # Two-column layout
    # -----------------------------

    left_column, right_column = st.columns(2)


    # -----------------------------
    # Left: Image
    # -----------------------------

    with left_column:

        st.subheader("Uploaded Image")

        processed_image = preprocess_image(temp_path)

        st.image(
            uploaded_file,
            width="stretch"
        )

        st.subheader("Preprocessed Image")

        processed_image = preprocess_image(temp_path)

        st.image(
        processed_image,
        caption="2× upscaled, grayscale, and denoised",
        width="stretch"
    )


    # -----------------------------
    # Right: OCR
    # -----------------------------

    with right_column:

        st.subheader("Recognized Text")

        extract_button = st.button(
            "Extract Dzongkha Text",
            type="primary"
        )

        if extract_button:

            with st.spinner("Processing image..."):

                text = extract_text(temp_path)

            st.text_area(
                "OCR Output",
                text,
                height=400
            )

            st.download_button(
                label="Download Text",
                data=text,
                file_name="dzongkha_ocr.txt",
                mime="text/plain"
            )


    # -----------------------------
    # Clean up temporary file
    # -----------------------------

    if os.path.exists(temp_path):
        os.remove(temp_path)