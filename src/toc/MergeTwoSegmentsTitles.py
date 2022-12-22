from copy import deepcopy
from typing import List

from src.toc.TitleFeatures import TitleFeatures
from src.toc.PdfFeatures.TocPdfFeatures import TocPdfFeatures


class MergeTwoSegmentsTitles:
    def __init__(self, pdf_features: TocPdfFeatures):
        self.pdf_features = deepcopy(pdf_features)
        titles_types: List[TitleFeatures] = TitleFeatures.from_pdf_features(self.pdf_features)
        self.titles_types_sorted = sorted(titles_types, key=lambda x: (x.pdf_segment.page_number, x.top))
        self.titles_merged: List[TitleFeatures] = list()
        self.run()

    def run(self):
        index = 0
        while index < len(self.titles_types_sorted):
            if index == len(self.titles_types_sorted) - 1:
                self.titles_merged.append(self.titles_types_sorted[index])
                break

            if not self.should_merge(self.titles_types_sorted[index], self.titles_types_sorted[index + 1]):
                self.titles_merged.append(self.titles_types_sorted[index])
                index += 1
                continue

            self.titles_types_sorted[index + 1] = self.titles_types_sorted[index + 1].append(self.titles_types_sorted[index])
            index += 1

    @staticmethod
    def should_merge(title: TitleFeatures, other_title: TitleFeatures):
        same_page = other_title.pdf_segment.page_number == title.pdf_segment.page_number

        if not same_page:
            return False

        if abs(other_title.top - title.bottom) > 15:
            return False

        if max(other_title.top, title.top) < min(other_title.bottom, title.bottom):
            return True

        if title.first_characters_type in [1, 2, 3] and other_title.first_characters_type in [1, 2, 3]:
            return False

        if title.bullet_points_type and other_title.bullet_points_type:
            return False

        if title.get_features_to_merge() != other_title.get_features_to_merge():
            return False

        return True
