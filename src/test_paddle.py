from paddleocr import PaddleOCR

# Try the Tibetan recognition model
ocr = PaddleOCR(
    lang="bod",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

result = ocr.predict("images/sample.jpeg")

for page in result:
    print(page["rec_texts"])