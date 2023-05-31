from statistics import mode

from data.PdfScript import PdfScript, ScriptsType
from data.SegmentBox import SegmentBox
from data.SegmentType import SegmentType
from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag
from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class PdfSegment:
    def __init__(
        self,
        page_number: int,
        segment_pdf_tags: list[PdfTag],
        bounding_box: Rectangle,
        text_content: str,
    ):
        self.page_number = page_number
        self.segment_pdf_tags: list[PdfTag] = segment_pdf_tags
        self.bounding_box = bounding_box
        self.text_content = text_content
        self.word_tags: list[PdfTag] = [word_tag for tag in self.segment_pdf_tags for word_tag in tag.word_tags]

    @staticmethod
    def from_segment(segment_pdf_tags: list[PdfTag]):
        text: str = " ".join([tag.content for tag in segment_pdf_tags])
        return PdfSegment(segment_pdf_tags[0].page_number, segment_pdf_tags, Rectangle.from_pdftags(segment_pdf_tags), text)

    def get_script(self, set_tag: PdfTag, text_before: str):
        line_tags = [tag for tag in self.word_tags if tag.same_line(set_tag)]
        font_size_mode = mode([tag.font.font_size for tag in line_tags])

        if set_tag.font.font_size >= font_size_mode:
            return

        top_mode = mode([tag.bounding_box.top for tag in line_tags])
        bottom_mode = mode([tag.bounding_box.bottom for tag in line_tags])

        start_character = len(text_before)
        end_character = start_character + len(set_tag.content) + 1
        if set_tag.bounding_box.bottom < bottom_mode:
            return PdfScript(type=ScriptsType.SUPER_SCRIPT, start_character=start_character, end_character=end_character)

        if top_mode < set_tag.bounding_box.top:
            return PdfScript(type=ScriptsType.SUB_SCRIPT, start_character=start_character, end_character=end_character)

    def to_segment_box(self) -> "SegmentBox":
        types = [tag.tag_type for tag in self.segment_pdf_tags]
        segment_type_string = mode(types) if types else ""

        scripts = list()
        text = ""
        for tag in self.word_tags:
            script = self.get_script(tag, text)

            if script:
                scripts.append(script)

            text = f"{text} {tag.content}" if text else tag.content

        return SegmentBox(
            left=self.bounding_box.left,
            top=self.bounding_box.top,
            width=self.bounding_box.width,
            height=self.bounding_box.height,
            page_number=self.page_number,
            text=text,
            type=SegmentType.from_string(segment_type_string),
            scripts=scripts,
        )
