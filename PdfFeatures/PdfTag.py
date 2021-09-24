from typing import List

from bs4 import Tag

from PdfFeatures.PdfFont import PdfFont
from PdfFeatures.Rectangle import Rectangle


class PdfTag:
    def __init__(self, page_number, tag_id: str, content: str, pdf_font: PdfFont,
                 reading_order_no: int, segment_no: int, bounding_box: Rectangle):
        self.page_number = int(page_number)
        self.id: str = tag_id
        self.content: str = content
        self.font: PdfFont = pdf_font
        self.reading_order_no: int = reading_order_no
        self.segment_no: int = segment_no
        self.bounding_box: Rectangle = bounding_box

    @staticmethod
    def from_pdfalto(page_number: int, xml_tag: Tag, fonts: List[PdfFont]):
        font_ids = [x['STYLEREFS'] for x in xml_tag.find_all('String') if 'STYLEREFS' in x.attrs]
        if len(font_ids) > 0 and len([x for x in fonts if x.font_id == font_ids[-1]]) > 0:
            pdf_font = [x for x in fonts if x.font_id == font_ids[-1]][0]
        else:
            pdf_font = None

        tag_id = xml_tag['ID']
        content = ' '.join([x['CONTENT'] for x in xml_tag.contents if 'CONTENT' in x.attrs])
        reading_order_no = int(xml_tag['ACTUAL_READING_ORDER']) if 'ACTUAL_READING_ORDER' in xml_tag.attrs else -1
        segment_no = int(xml_tag['GROUP']) if 'GROUP' in xml_tag.attrs else -1
        bounding_box = Rectangle.from_tag(xml_tag)
        return PdfTag(page_number, tag_id, content, pdf_font, reading_order_no, segment_no, bounding_box)
