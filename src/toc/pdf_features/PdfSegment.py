from statistics import mode


from data.SegmentBox import SegmentBox
from data.SegmentType import SegmentType
from extract_pdf_paragraphs.pdf_features.Rectangle import Rectangle
from src.toc.pdf_features.PdfTag import PdfTag

from src.toc.pdf_features.TagType import TagType

from src.toc.pdf_features.PdfAnnotation import PdfAnnotation


class PdfSegment:
    def __init__(
        self,
        page_number: int,
        bounding_box: Rectangle,
        text_content: str,
    ):
        self.page_number = page_number
        self.bounding_box = bounding_box
        self.text_content = text_content
        self.ml_label = 0
        self.ml_percentage = 0
        self.segment_type = 6
        self.embeddings = []
        self.multilingual_embeddings = []
        self.index = 0

    def is_selected(self, bounding_box: Rectangle):
        if bounding_box.bottom < self.bounding_box.top or self.bounding_box.bottom < bounding_box.top:
            return False

        if bounding_box.right < self.bounding_box.left or self.bounding_box.right < bounding_box.left:
            return False

        return True

    def intersects(self, pdf_segment: "PdfSegment"):
        if self.page_number != pdf_segment.page_number:
            return False

        return self.is_selected(pdf_segment.bounding_box)

    def set_type_from_tag_types(self, tag_types: list[TagType]):
        segment_tag_types: list[TagType] = list()
        for tag_type in tag_types:
            if self.page_number != tag_type.page_number:
                continue

            if self.is_selected(tag_type.bounding_box):
                segment_tag_types.append(tag_type)

        if segment_tag_types:
            self.segment_type = mode([x.tag_type_index for x in segment_tag_types])

    def set_ml_label_from_annotations(self, annotations: list[PdfAnnotation]):
        for annotation in annotations:
            if self.page_number != annotation.page_number:
                continue

            if self.is_selected(annotation.bounds):
                self.ml_label = 1
                return

    @staticmethod
    def from_segment_dict(index, segment_dict) -> "PdfSegment":
        return PdfSegment(
            page_number=segment_dict["page_number"],
            segment_ids=index,
            bounding_box=Rectangle.from_segment_dict(segment_dict),
            text_content=segment_dict["text"],
        )

    @staticmethod
    def from_segment_box(segment_box: SegmentBox) -> "PdfSegment":
        return PdfSegment(
            page_number=segment_box.page_number,
            bounding_box=Rectangle.from_segment_box(segment_box),
            text_content="",
        )

    @staticmethod
    def from_pdf_tag(pdf_tag: PdfTag):
        return PdfSegment(page_number=pdf_tag.page_number, bounding_box=pdf_tag.bounding_box, text_content=pdf_tag.content)

    @staticmethod
    def from_list_to_merge(pdf_segments_to_merge: list["PdfSegment"]):
        text_content = " ".join([pdf_segment.text_content for pdf_segment in pdf_segments_to_merge])
        bounding_box = Rectangle.merge_rectangles([pdf_segment.bounding_box for pdf_segment in pdf_segments_to_merge])
        return PdfSegment(
            page_number=pdf_segments_to_merge[0].page_number, bounding_box=bounding_box, text_content=text_content
        )

    def get_segment_box(self):
        return SegmentBox(
            left=self.bounding_box.left,
            top=self.bounding_box.top,
            width=self.bounding_box.width,
            height=self.bounding_box.height,
            page_number=self.page_number,
        )

    def to_segment_box(self) -> "SegmentBox":
        return SegmentBox(
            left=self.bounding_box.left,
            top=self.bounding_box.top,
            width=self.bounding_box.width,
            height=self.bounding_box.height,
            page_number=self.page_number,
            text=self.text_content,
            type=SegmentType.TITLE,
            scripts=list(),
        )
