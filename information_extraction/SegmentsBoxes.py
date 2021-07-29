import json
from typing import List

from information_extraction.InformationExtraction import InformationExtraction
from information_extraction.Segment import Segment


class SegmentBox:
    def __init__(self, left, top, width, height, page_number):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.page_number = page_number

    @staticmethod
    def from_segment(segment: Segment) -> 'SegmentBox':
        return SegmentBox(segment.left, segment.top, segment.width, segment.height, segment.page_number)

    def to_dictionary(self):
        return {"left": self.left, "top": self.top, "width": self.width, "height": self.height, "pageNumber": self.page_number}


class SegmentsBoxes:
    def __init__(self, segment_boxes: List[SegmentBox]):
        self.segment_boxes = segment_boxes

    def to_json(self):
        return json.dumps([segment_box.to_dictionary() for segment_box in self.segment_boxes])

    @staticmethod
    def from_information_extraction(information_extraction: InformationExtraction) -> 'SegmentsBoxes':
        return SegmentsBoxes([SegmentBox.from_segment(segment) for segment in information_extraction.segments])