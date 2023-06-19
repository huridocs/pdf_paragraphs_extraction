from copy import deepcopy


from extract_pdf_paragraphs.pdf_features.PdfSegment import PdfSegment
from src.toc.MergeTwoSegmentsTitles import MergeTwoSegmentsTitles
from src.toc.TitleFeatures import TitleFeatures
from src.toc.data.TOCItem import TOCItem
from src.toc.methods.two_models_v3_segments_context_2.TwoModelsV3SegmentsContext2 import TwoModelsV3SegmentsContext2
from src.toc.pdf_features.TocPdfFeatures import TocPdfFeatures

two_models = TwoModelsV3SegmentsContext2()


class TOC:
    def __init__(self, pdf_features: TocPdfFeatures):
        pdf_features_copy = deepcopy(pdf_features)
        self.pdf_features = two_models.predict([pdf_features_copy])[0]
        self.titles_features_sorted = MergeTwoSegmentsTitles(self.pdf_features).titles_merged
        self.toc: list[TOCItem] = list()
        self.set_toc()

    def set_toc(self):
        for index, title_features in enumerate(self.titles_features_sorted):
            indentation = self.get_indentation(index, title_features)
            self.toc.append(title_features.to_toc_item(indentation))

    def __str__(self):
        return "\n".join([f'{"  " * x.indentation} * {x.label}' for x in self.toc])

    def get_indentation(self, title_index: int, title_features: TitleFeatures):
        if title_index == 0:
            return 0

        for index in reversed(range(title_index)):
            if self.toc[index].point_closed:
                continue

            if self.same_indentation(self.titles_features_sorted[index], title_features):
                self.close_toc_items(self.toc[index].indentation)
                return self.toc[index].indentation

        return self.toc[title_index - 1].indentation + 1

    def close_toc_items(self, indentation):
        for toc in self.toc:
            if toc.indentation > indentation:
                toc.point_closed = True

    @staticmethod
    def from_pdf_tags(xml_tags: str, pdf_segments: list[PdfSegment]):
        toc_pdf_features = TocPdfFeatures.from_xml_content(xml_tags)
        toc_pdf_features.set_segments_from_pdf_segments(pdf_segments)
        return TOC(toc_pdf_features)

    @staticmethod
    def same_indentation(previous_title_features: TitleFeatures, title_features: TitleFeatures):
        if previous_title_features.first_characters in title_features.get_possible_previous_point():
            return True

        if previous_title_features.get_features_toc() == title_features.get_features_toc():
            return True

        return False

    def to_dict(self):
        toc: list[dict[str, any]] = list()

        for toc_item in self.toc:
            toc_element_dict = dict()
            toc_element_dict["indentation"] = toc_item.indentation
            toc_element_dict["label"] = toc_item.label
            toc_element_dict["selectionRectangles"] = list()
            for selection_rectangle in toc_item.selectionRectangles:
                rectangle = dict()
                rectangle["left"] = int(selection_rectangle.left / 0.75)
                rectangle["top"] = int(selection_rectangle.top / 0.75)
                rectangle["width"] = int(selection_rectangle.width / 0.75)
                rectangle["height"] = int(selection_rectangle.height / 0.75)
                rectangle["page"] = str(selection_rectangle.page_number)
                toc_element_dict["selectionRectangles"].append(rectangle)
            toc.append(toc_element_dict)

        return toc
