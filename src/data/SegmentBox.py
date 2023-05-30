from statistics import mode

from pydantic import BaseModel

from data.PdfScript import PdfScript, ScriptsType
from data.SegmentType import SegmentType
from extract_pdf_paragraphs.PdfFeatures import PdfTag
from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment

SCALE_CONSTANT = 0.75


class SegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int
    text: str = ""
    type: SegmentType = SegmentType.TEXT
    scripts: list[PdfScript] = list()

    class Config:
        use_enum_values = True

    @staticmethod
    def get_script(set_tag: PdfTag, word_tags: list[PdfTag], text_before: str):
        line_tags = [tag for tag in word_tags if tag.same_line(set_tag)]
        font_size_mode = mode([tag.font.font_size for tag in line_tags])

        if set_tag.font.font_size >= font_size_mode:
            return

        top_mode = mode([tag.bounding_box.top for tag in line_tags])
        bottom_mode = mode([tag.bounding_box.bottom for tag in line_tags])

        if set_tag.bounding_box.bottom < bottom_mode:
            return PdfScript(
                type=ScriptsType.SUPER_SCRIPT, start=len(text_before), end=len(text_before) + len(set_tag.content)
            )

        if top_mode < set_tag.bounding_box.top:
            return PdfScript(
                type=ScriptsType.SUB_SCRIPT, start=len(text_before), end=len(text_before) + len(set_tag.content)
            )

    @staticmethod
    def from_pdf_segment(segment: PdfSegment) -> "SegmentBox":
        types = [tag.tag_type for tag in segment.segment_pdf_tags]
        segment_type_string = mode(types) if types else ""

        all_word_tags: list[PdfTag] = [word_tag for tag in segment.segment_pdf_tags for word_tag in tag.word_tags]

        scripts = list()
        text = ""
        for tag in all_word_tags:
            script = SegmentBox.get_script(tag, all_word_tags, text)

            if script:
                scripts.append(script)

            text = f"{text} {tag.content}" if text else tag.content

        return SegmentBox(
            left=segment.bounding_box.left,
            top=segment.bounding_box.top,
            width=segment.bounding_box.width,
            height=segment.bounding_box.height,
            page_number=segment.page_number,
            text=text,
            type=SegmentType.from_string(segment_type_string),
            scripts=scripts,
        )

    def correct_input_data_scale(self):
        return self.rescaled(SCALE_CONSTANT, SCALE_CONSTANT)

    def correct_output_data_scale(self):
        return self.rescaled(1 / SCALE_CONSTANT, 1 / SCALE_CONSTANT)

    def rescaled(self, factor_width: float, factor_height: float):
        self.left = self.left * factor_width
        self.top = self.top * factor_height
        self.width = self.width * factor_width
        self.height = self.height * factor_height
        return self

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
        }


if __name__ == "__main__":
    box = SegmentBox(left=1, top=1, width=1, height=1, page_number=1, text="1", tag_type=SegmentType.from_index(1))
    print(box.dict())
