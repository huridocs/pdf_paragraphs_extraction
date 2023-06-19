from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class TOCItem(BaseModel):
    indentation: int
    label: str = ""
    selectionRectangles: list[SegmentBox]
    point_closed: bool = False

    def correct_data_scale(self):
        self.selectionRectangles = [x.correct_input_data_scale() for x in self.selectionRectangles]
        return self
