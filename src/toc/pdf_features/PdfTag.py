from bs4 import Tag, NavigableString

from src.toc.pdf_features.PdfFont import PdfFont

from extract_pdf_paragraphs.pdf_features.Rectangle import Rectangle
from data.SegmentBox import SegmentBox


class PdfTag:
    def __init__(
        self,
        page_number: int,
        tag_id: str,
        content: str,
        pdf_font: PdfFont,
        reading_order_no: int,
        segment_no: int,
        bounding_box: Rectangle,
        tag_type: str = "pad_type",
    ):
        self.page_number = page_number
        self.id: str = tag_id
        self.content: str = content
        self.font: PdfFont = pdf_font
        self.reading_order_no: int = reading_order_no
        self.segment_no: int = segment_no
        self.bounding_box: Rectangle = bounding_box
        self.tag_type: str = tag_type

    @staticmethod
    def from_pdfalto(page_number: str, xml_tag: Tag, fonts: list[PdfFont]):
        font_ids = [x["STYLEREFS"] for x in xml_tag.find_all("String") if "STYLEREFS" in x.attrs]
        if len(font_ids) > 0 and len([x for x in fonts if x.font_id == font_ids[-1]]) > 0:
            pdf_font = [x for x in fonts if x.font_id == font_ids[-1]][0]
        else:
            pdf_font = None

        tag_id = xml_tag["ID"]
        content = " ".join(
            [x["CONTENT"] for x in xml_tag.contents if not isinstance(x, NavigableString) and "CONTENT" in x.attrs]
        )
        reading_order_no = (
            int(xml_tag["ACTUAL_READING_ORDER"])
            if not isinstance(xml_tag, NavigableString) and "ACTUAL_READING_ORDER" in xml_tag.attrs
            else -1
        )
        segment_no = int(xml_tag["GROUP"]) if "GROUP" in xml_tag.attrs else -1
        bounding_box = Rectangle.from_tag(xml_tag)
        return PdfTag(int(page_number), tag_id, content, pdf_font, reading_order_no, segment_no, bounding_box)

    def to_segment_box(self) -> SegmentBox:
        return SegmentBox(
            left=self.bounding_box.left,
            top=self.bounding_box.top,
            width=self.bounding_box.width,
            height=self.bounding_box.height,
            page_number=self.page_number,
        )
