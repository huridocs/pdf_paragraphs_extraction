from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox
from information_extraction.Segment import Segment


class ExtractionData(BaseModel):
    tenant: str
    pdf_file_name: str
    paragraphs: List[SegmentBox]

    @staticmethod
    def from_segments(tenant: str, pdf_file_name: str, segments: List[Segment]):
        paragraphs_boxes = [SegmentBox.from_segment(x) for x in segments]
        return ExtractionData(tenant=tenant,
                              pdf_file_name=pdf_file_name,
                              paragraphs=paragraphs_boxes)
