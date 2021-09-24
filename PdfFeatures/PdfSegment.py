from typing import List

from PdfFeatures.Rectangle import Rectangle


class PdfSegment:
    def __init__(self, page_number: int, segment_ids: List[str], bounding_box: Rectangle, text_content: str):
        self.page_number = page_number
        self.segment_ids = segment_ids
        self.bounding_box = bounding_box
        self.text_content = text_content
