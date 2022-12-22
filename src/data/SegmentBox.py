from pydantic import BaseModel

from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment

SCALE_CONSTANT = 0.75


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""

    @staticmethod
    def from_pdf_segment(segment: PdfSegment) -> "SegmentBox":
        return SegmentBox(
            left=segment.bounding_box.left,
            top=segment.bounding_box.top,
            width=segment.bounding_box.width,
            height=segment.bounding_box.height,
            page_number=segment.page_number,
            text=segment.text_content,
        )

    def correct_input_data_scale(self):
        return self.rescaled(SCALE_CONSTANT, SCALE_CONSTANT)

    def correct_output_data_scale(self):
        return self.rescaled(1 / SCALE_CONSTANT, 1 / SCALE_CONSTANT)

    def rescaled(self, factor_width: float, factor_height: float):
        self.left = self.left * factor_width
        self.top = self.top * factor_height
        self.width = self.width * factor_width
        self.height = self.height * factor_height
        return self

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
        }
