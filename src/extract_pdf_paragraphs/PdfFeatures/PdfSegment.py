from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag
from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class PdfSegment:
    def __init__(
        self,
        page_number: int,
        segment_pdf_tags: list[PdfTag],
        bounding_box: Rectangle,
        text_content: str,
    ):
        self.page_number = page_number
        self.segment_pdf_tags: list[PdfTag] = segment_pdf_tags
        self.bounding_box = bounding_box
        self.text_content = text_content

    @staticmethod
    def from_segment(segment_pdf_tags: list[PdfTag]):
        text: str = " ".join([tag.content for tag in segment_pdf_tags])
        return PdfSegment(segment_pdf_tags[0].page_number, segment_pdf_tags, Rectangle.from_pdftags(segment_pdf_tags), text)
