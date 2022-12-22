from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox
from src.toc.data.SegmentationData import SegmentationData


class ExtractionData(BaseModel):
    paragraphs: List[SegmentBox]
    page_height: int
    page_width: int

    def to_segmentation(self) -> SegmentationData:
        return SegmentationData(page_width=self.page_width, page_height=self.page_height, xml_segments_boxes=self.paragraphs)
