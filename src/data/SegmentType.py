from enum import Enum

from extract_pdf_paragraphs.tag_type_finder.LightGBM_30Features_OneHotOneLetter import tag_type_dict


class SegmentType(str, Enum):
    FORMULA = "FORMULA"
    FOOTNOTE = "FOOTNOTE"
    LIST = "LIST"
    TABLE = "TABLE"
    FIGURE = "FIGURE"
    TITLE = "TITLE"
    TEXT = "TEXT"

    @staticmethod
    def from_index(index: int):
        option_list = [e for e in SegmentType]
        if 0 <= index < len(option_list):
            return option_list[index]

        return SegmentType.TEXT

    @staticmethod
    def from_string(type_name: str):
        indexes = [value for key, value in tag_type_dict.items() if key == type_name]

        if indexes:
            return SegmentType.from_index(indexes[0])

        return SegmentType.from_index(-1)

    def __dict__(self):
        return self.value