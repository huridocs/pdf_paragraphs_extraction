from statistics import mode

from pydantic import BaseModel

from data.SegmentType import SegmentType
from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment

SCALE_CONSTANT = 0.75


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""
    tag_type: SegmentType

    class Config:
        use_enum_values = True

    @staticmethod
    def from_pdf_segment(segment: PdfSegment) -> "SegmentBox":
        types = [tag.tag_type for tag in segment.segment_pdf_tags]
        segment_type_string = mode(types) if types else ""

        return SegmentBox(
            left=segment.bounding_box.left,
            top=segment.bounding_box.top,
            width=segment.bounding_box.width,
            height=segment.bounding_box.height,
            page_number=segment.page_number,
            text=segment.text_content,
            tag_type=SegmentType.from_string(segment_type_string)
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


if __name__ == '__main__':
    box = SegmentBox(left=1, top=1, width=1, height=1, page_number=1, text="1", tag_type=SegmentType.from_index(1))
    print(box.dict())