from src.toc.pdf_features.PdfTag import PdfTag

from extract_pdf_paragraphs.pdf_features.Rectangle import Rectangle

TAG_TYPE_DICT: dict = {
    "text": 6,
    "title": 5,
    "figure": 4,
    "table": 3,
    "list": 2,
    "footnote": 1,
    "formula": 0,
    "code": 3,
}

TAG_TYPE_BY_INDEX: dict = {value: key for key, value in TAG_TYPE_DICT.items()}


class TagType:
    def __init__(self, tag: PdfTag, tag_type: str):
        self.bounding_box: Rectangle = tag.bounding_box
        self.tag_type = tag_type
        self.page_number = tag.page_number
        self.tag_type_index = TAG_TYPE_DICT[tag_type]
