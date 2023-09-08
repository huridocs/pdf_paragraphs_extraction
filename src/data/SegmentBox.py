from extract_pdf_paragraphs.PdfSegment import PdfSegment
from pdf_features.PdfToken import PdfToken
from pdf_token_type_labels.TokenType import TokenType
from pydantic import BaseModel

from data.PdfScript import PdfScript


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""
    type: TokenType = TokenType.TEXT
    scripts: list[PdfScript] = list()

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
        }

    @staticmethod
    def from_pdf_segment(pdf_segment: PdfSegment):
        return SegmentBox(
            left=pdf_segment.bounding_box.left,
            top=pdf_segment.bounding_box.top,
            width=pdf_segment.bounding_box.width,
            height=pdf_segment.bounding_box.height,
            page_number=pdf_segment.page_number,
            text=pdf_segment.text_content,
            type=pdf_segment.segment_type,
            scripts=[],
        )

    @staticmethod
    def from_pdf_token(pdf_token: PdfToken):
        return SegmentBox(
            left=pdf_token.bounding_box.left,
            top=pdf_token.bounding_box.top,
            width=pdf_token.bounding_box.width,
            height=pdf_token.bounding_box.height,
            page_number=pdf_token.page_number,
            text=pdf_token.content,
            type=pdf_token.token_type,
            scripts=[],
        )
