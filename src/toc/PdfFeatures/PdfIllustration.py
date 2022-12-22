from bs4 import Tag

from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class PdfIllustration:
    def __init__(
        self,
        page_number: int,
        bounding_box: Rectangle,
    ):
        self.page_number = int(page_number)
        self.bounding_box: Rectangle = bounding_box

    @staticmethod
    def from_pdfalto(page_number: str, illustration_tag: Tag):
        bounding_box = Rectangle.from_tag(illustration_tag)
        return PdfIllustration(
            int(page_number),
            bounding_box,
        )
