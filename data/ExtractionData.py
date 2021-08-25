from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox
from information_extraction.Segment import Segment


class ExtractionData(BaseModel):
    tenant: str
    xml_file_name: str
    paragraphs_boxes: List[SegmentBox]

    @staticmethod
    def from_segments(tenant: str, xml_file_name: str, segments: List[Segment]):
        paragraphs_boxes = [SegmentBox.from_segment(x) for x in segments]
        return ExtractionData(tenant=tenant, xml_file_name=xml_file_name, paragraphs_boxes=paragraphs_boxes)
