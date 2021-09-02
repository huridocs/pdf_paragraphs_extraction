from typing import List

from extract_pdf_paragraphs.information_extraction.SegmentTag import SegmentTag
from extract_pdf_paragraphs.pdfalto.PDFFeatures import PDFFeatures


class Segment:
    def __init__(self, segment_tags: List[SegmentTag], pdf_features: PDFFeatures, page_number: int):
        self.page_number = page_number
        self.segment_tags = segment_tags
        self.pdf_features = pdf_features
        self.images = pdf_features.page_images[page_number]
        self.page_width = self.pdf_features.page_width
        self.page_height = self.pdf_features.page_height
        self.text_content: str = ''
        self.text_len: int = 0
        self.top: float = 0
        self.left: float = 0
        self.right: float = 0
        self.bottom: float = 0
        self.height: float = 0
        self.width: float = 0
        self.set_features()

    def set_features(self):
        self.top = self.segment_tags[0].top
        self.left = self.segment_tags[0].left
        self.right = self.segment_tags[0].left + self.segment_tags[0].width
        self.bottom = self.segment_tags[0].top + self.segment_tags[0].height
        words: List[str] = list()

        for tag in self.segment_tags:
            words.extend(tag.text.split())
            self.top = min(self.top, tag.top)
            self.left = min(self.left, tag.left)
            self.right = max(self.right, tag.left + tag.width)
            self.bottom = max(self.bottom, tag.top + tag.height)

        self.top = self.top
        self.bottom = self.bottom
        self.right = self.right
        self.left = self.left

        self.text_content = ' '.join(words)
        self.text_len = len(self.text_content)
        self.height = self.bottom - self.top
        self.width = self.right - self.left
