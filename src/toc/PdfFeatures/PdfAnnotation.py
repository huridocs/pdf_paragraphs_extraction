from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class PdfAnnotation:
    LABELS_FILE_NAME = "development_user@example.com_annotations.json"

    def __init__(self, page_number: int, bounds: Rectangle):
        self.page_number = page_number
        self.bounds = bounds
