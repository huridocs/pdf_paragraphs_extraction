from pydantic import BaseModel

from extract_pdf_paragraphs.information_extraction.Segment import Segment


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str

    @staticmethod
    def from_segment(segment: Segment) -> 'SegmentBox':
        return SegmentBox(left=segment.left,
                          top=segment.top,
                          width=segment.width,
                          height=segment.height,
                          page_number=segment.page_number,
                          text=segment.text_content)
