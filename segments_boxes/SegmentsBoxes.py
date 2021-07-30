import json
from typing import List

from information_extraction.InformationExtraction import InformationExtraction
from information_extraction.Segment import Segment


class SegmentBox:
    def __init__(self, text, left, top, width, height, page_number):
        self.text = text
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.page_number = page_number

    @staticmethod
    def from_segment(segment: Segment) -> 'SegmentBox':
        return SegmentBox(segment.text_content,
                          segment.left,
                          segment.top,
                          segment.width,
                          segment.height,
                          segment.page_number)

    def to_dictionary(self):
        return {"text": self.text, "left": self.left, "top": self.top, "width": self.width, "height": self.height,
                "pageNumber": self.page_number}


class SegmentsBoxes:
    def __init__(self, page_width, page_height, segment_boxes: List[SegmentBox], ):
        self.page_width = page_width
        self.page_height = page_height
        self.segment_boxes = segment_boxes

    def to_json(self):
        segments = [segment_box.to_dictionary() for segment_box in self.segment_boxes]
        segments_boxes_json = {"pageWidth": self.page_width, "pageHeight": self.page_height, "segments": segments}
        return json.dumps(segments_boxes_json)

    @staticmethod
    def from_information_extraction(information_extraction: InformationExtraction) -> 'SegmentsBoxes':
        if not len(information_extraction.segments):
            return SegmentsBoxes(information_extraction.pdf_features.page_width,
                                 information_extraction.pdf_features.page_height, [])

        segment_boxes = [SegmentBox.from_segment(segment) for segment in information_extraction.segments]

        return SegmentsBoxes(information_extraction.pdf_features.page_width,
                             information_extraction.pdf_features.page_height, segment_boxes)
