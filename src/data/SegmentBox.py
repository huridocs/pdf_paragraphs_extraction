from pydantic import BaseModel

from data.PdfScript import PdfScript
from data.SegmentType import SegmentType

SCALE_CONSTANT = 0.75


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""
    type: SegmentType = SegmentType.TEXT
    scripts: list[PdfScript] = list()

    class Config:
        use_enum_values = True

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
