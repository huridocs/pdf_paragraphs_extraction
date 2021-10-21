from pydantic import BaseModel

from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str

    @staticmethod
    def from_pdf_segment(segment: PdfSegment) -> 'SegmentBox':
        return SegmentBox(left=segment.bounding_box.left,
                          top=segment.bounding_box.top,
                          width=segment.bounding_box.width,
                          height=segment.bounding_box.height,
                          page_number=segment.page_number,
                          text=segment.text_content)
