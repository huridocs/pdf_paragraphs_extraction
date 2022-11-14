from typing import List

from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag
from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class PdfSegment:
    def __init__(
        self,
        page_number: int,
        segment_ids: List[str],
        bounding_box: Rectangle,
        text_content: str,
    ):
        self.page_number = page_number
        self.segment_ids = segment_ids
        self.bounding_box = bounding_box
        self.text_content = text_content

    @staticmethod
    def from_segment(pdf_tags: List[PdfTag]):
        segment_ids = [tag.id for tag in pdf_tags]
        text: str = ' '.join([tag.content for tag in pdf_tags])
        return PdfSegment(pdf_tags[0].page_number, segment_ids, Rectangle.from_pdftags(pdf_tags), text)
