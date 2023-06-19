from unittest import TestCase

from data.PdfScript import PdfScript, ScriptsType
from data.SegmentType import SegmentType
from extract_pdf_paragraphs.pdf_features.PdfFont import PdfFont
from extract_pdf_paragraphs.pdf_features.PdfSegment import PdfSegment
from extract_pdf_paragraphs.pdf_features.PdfTag import PdfTag
from extract_pdf_paragraphs.pdf_features.Rectangle import Rectangle


class TestPdfSegment(TestCase):
    def test_to_segment_box(self):
        pdf_tags = []
        rectangle = Rectangle(left=1, top=2, right=3, bottom=4)
        pdf_segment = PdfSegment(page_number=1, segment_pdf_tags=pdf_tags, bounding_box=rectangle, text_content="one two")
        segment_box = pdf_segment.to_segment_box()

        self.assertEqual(1, segment_box.left)
        self.assertEqual(2, segment_box.top)
        self.assertEqual(2, segment_box.width)
        self.assertEqual(2, segment_box.height)
        self.assertEqual(1, segment_box.page_number)
        self.assertEqual(SegmentType.TEXT, segment_box.type)
        self.assertEqual([], segment_box.scripts)

    def test_to_segment_box_type(self):
        rectangle = Rectangle(left=1, top=2, right=3, bottom=4)
        pdf_tags = [
            PdfTag(
                page_number=3,
                tag_id="id",
                content="content",
                pdf_font=PdfFont(font_id="id", bold=False, italics=False, font_size=10),
                reading_order_no=0,
                segment_no=0,
                bounding_box=rectangle,
                tag_type="footnote",
                word_tags=[],
            )
        ]

        rectangle = Rectangle(left=1, top=2, right=3, bottom=4)
        pdf_segment = PdfSegment(page_number=3, segment_pdf_tags=pdf_tags, bounding_box=rectangle, text_content="one two")
        segment_box = pdf_segment.to_segment_box()

        self.assertEqual(3, segment_box.page_number)
        self.assertEqual(SegmentType.FOOTNOTE, segment_box.type)

    @staticmethod
    def create_tag(rectangle: Rectangle, font_size: float):
        return PdfTag(
            page_number=10,
            tag_id="id",
            content="content",
            pdf_font=PdfFont(font_id="id", bold=False, italics=False, font_size=font_size),
            reading_order_no=0,
            segment_no=0,
            bounding_box=rectangle,
            tag_type="title",
            word_tags=[],
        )

    def test_no_superscripts(self):
        rectangle = Rectangle(left=1, top=2, right=3, bottom=4)

        word_tag_1 = self.create_tag(rectangle, 10)
        word_tag_2 = self.create_tag(rectangle, 10)
        word_tag_3 = self.create_tag(rectangle, 10)

        pdf_tag = self.create_tag(rectangle, 10)
        pdf_tag.word_tags = [word_tag_1, word_tag_2, word_tag_3]
        pdf_tags = [self.create_tag(rectangle, 10)]
        pdf_segment = PdfSegment(page_number=1, segment_pdf_tags=pdf_tags, bounding_box=rectangle, text_content="one two")
        segment_box = pdf_segment.to_segment_box()

        self.assertEqual(SegmentType.TITLE, segment_box.type)
        self.assertEqual([], segment_box.scripts)

    def test_one_superscripts(self):
        rectangle = Rectangle(left=1, top=2, right=3, bottom=4)

        word_tag_1 = self.create_tag(rectangle, 10)
        word_tag_2 = self.create_tag(Rectangle(left=1, top=2, right=3, bottom=3), 9)
        word_tag_3 = self.create_tag(rectangle, 10)

        pdf_tag = self.create_tag(rectangle, 10)
        pdf_tag.word_tags = [word_tag_1, word_tag_2, word_tag_3]
        pdf_segment = PdfSegment(page_number=1, segment_pdf_tags=[pdf_tag], bounding_box=rectangle, text_content="one two")
        segment_box = pdf_segment.to_segment_box()

        self.assertEqual(SegmentType.TITLE, segment_box.type)
        self.assertEqual("content content content", segment_box.text)
        self.assertEqual(
            [PdfScript(start_character=7, end_character=15, type=ScriptsType.SUPER_SCRIPT)], segment_box.scripts
        )

    def test_two_subscripts(self):
        rectangle = Rectangle(left=1, top=6, right=3, bottom=8)

        word_tag_1 = self.create_tag(rectangle, 10)
        word_tag_2 = self.create_tag(Rectangle(left=1, top=7, right=3, bottom=8.5), 9)
        word_tag_3 = self.create_tag(rectangle, 10)
        word_tag_4 = self.create_tag(Rectangle(left=1, top=6.5, right=3, bottom=8), 9)

        pdf_tag = self.create_tag(rectangle, 10)
        pdf_tag.word_tags = [word_tag_1, word_tag_2, word_tag_3, word_tag_4]
        pdf_segment = PdfSegment(page_number=1, segment_pdf_tags=[pdf_tag], bounding_box=rectangle, text_content="one two")
        segment_box = pdf_segment.to_segment_box()

        self.assertEqual(SegmentType.TITLE, segment_box.type)
        self.assertEqual("content content content content", segment_box.text)
        self.assertEqual(2, len(segment_box.scripts))
        self.assertEqual(PdfScript(start_character=7, end_character=15, type=ScriptsType.SUB_SCRIPT), segment_box.scripts[0])
        self.assertEqual(
            PdfScript(start_character=23, end_character=31, type=ScriptsType.SUB_SCRIPT), segment_box.scripts[1]
        )
