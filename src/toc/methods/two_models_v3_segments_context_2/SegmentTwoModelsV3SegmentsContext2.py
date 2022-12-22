import re
from typing import List
import numpy as np

from src.toc.PdfFeatures.TocPdfFeatures import TocPdfFeatures
from src.toc.PdfFeatures.PdfSegment import PdfSegment
from src.toc.PdfFeatures.PdfTag import PdfTag
from src.toc.PdfFeatures.TagType import TAG_TYPE_DICT
from src.toc.methods.two_models_v3_segments_context_2.Modes import Modes


class SegmentTwoModelsV3SegmentsContext2:
    def __init__(
        self, segment_index: int, pdf_segment: PdfSegment, pdf_features: TocPdfFeatures, title_index: int, modes: Modes
    ):
        self.title_index = title_index
        self.modes = modes
        self.previous_title_segment = None
        self.context_segments: List["SegmentTwoModelsV3SegmentsContext2"] = list()
        self.sentence_embeddings = pdf_segment.multilingual_embeddings
        self.segment_index: float = segment_index
        self.confidence: float = 0
        self.page_number = pdf_segment.page_number
        self.page_index = pdf_segment.page_number - 1
        self.pdf_segment = pdf_segment
        self.segment_tags: List[PdfTag] = [
            pdf_tag
            for pdf_tag in pdf_features.get_tags()
            if self.page_number == pdf_tag.page_number and pdf_segment.is_selected(pdf_tag.bounding_box)
        ]

        self.segment_tags = self.segment_tags if self.segment_tags else [pdf_features.get_tags()[-1]]
        self.pdf_features = pdf_features
        self.page_width = self.pdf_features.pages[0].page_width
        self.page_height = self.pdf_features.pages[0].page_height
        self.text_content: str = ""
        self.text_len: int = 0
        self.font_size: float = 0.0
        self.font_family: str = ""
        self.font_color: str = ""
        self.line_height: int = 0
        self.numbers_quantity: int = 0
        self.numbers_percentage: float = 0
        self.starts_upper: bool = False
        self.starts_number: bool = False
        self.starts_number_bar: bool = False
        self.starts_letter_dot: bool = False
        self.uppercase: bool = False
        self.last_tag: PdfSegment = None
        self.bold: float = False
        self.bold_tag_number: int = 0
        self.italics: float = False
        self.italics_tag_number: int = 0
        self.first_word_type: int = 100
        self.second_word_type: int = 100
        self.third_word_type: int = 100
        self.fourth_word_type: int = 100
        self.last_word_type: int = 100
        self.dots_percentage: float = 0
        self.font_sizes = [x.font.font_size for x in self.pdf_features.get_tags()]
        self.first_characters_type = 0
        self.first_characters_special_markers_count = 0
        self.bullet_points_type = 0
        self.page_width = self.pdf_features.pages[0].page_width
        self.page_height = self.pdf_features.pages[0].page_height
        self.text_content: str = ""
        self.text_len: int = 0
        self.top: float = 0
        self.left: float = 0
        self.right: float = 0
        self.bottom: float = 0
        self.height: float = 0
        self.width: float = 0
        self.font_size: float = 0.0
        self.font_family: str = ""
        self.font_color: str = ""
        self.line_height: int = 0
        self.numbers_quantity: int = 0
        self.numbers_percentage: float = 0
        self.starts_upper: bool = False
        self.starts_number: bool = False
        self.starts_number_bar: bool = False
        self.starts_letter_dot: bool = False
        self.starts_with_square_brackets: bool = False
        self.starts_with_roman_numbers: bool = False
        self.uppercase: bool = False
        self.last_tag: PdfSegment = None
        self.bold: float = False
        self.bold_tag_number: int = 0
        self.italics: float = False
        self.italics_tag_number: int = 0
        self.first_word_type: int = 100
        self.second_word_type: int = 100
        self.third_word_type: int = 100
        self.fourth_word_type: int = 100
        self.last_word_type: int = 100
        self.dots_percentage: float = 0

        self.font_family = self.segment_tags[0].font.font_id
        self.font_color = self.segment_tags[0].font.color
        self.line_height = self.segment_tags[0].font.font_size
        self.top = self.segment_tags[0].bounding_box.top
        self.left = self.segment_tags[0].bounding_box.left
        self.right = self.segment_tags[0].bounding_box.right
        self.bottom = self.segment_tags[0].bounding_box.bottom
        words: List[str] = list()

        font_sizes = list()
        for tag in self.segment_tags:
            words.extend(tag.content.split())
            self.top = min(self.top, tag.bounding_box.top)
            self.left = min(self.left, tag.bounding_box.left)
            self.right = max(self.right, tag.bounding_box.left + tag.bounding_box.width)
            self.bottom = max(self.bottom, tag.bounding_box.top + tag.bounding_box.height)
            self.bold_tag_number = self.bold_tag_number + 1 if tag.font.bold else self.bold_tag_number
            self.italics_tag_number = self.italics_tag_number + 1 if tag.font.italics else self.italics_tag_number
            font_sizes.append(tag.font.font_size)
            if self.tag_after_last_tag(tag):
                self.last_tag = tag

        self.top = self.top
        self.bottom = self.bottom
        self.right = self.right
        self.left = self.left
        self.text_content = " ".join(words)
        self.text_len = len(self.text_content)
        self.dots_percentage = self.text_content.count(".") / self.text_len if self.text_len > 0 else 0
        self.height = self.bottom - self.top
        self.width = self.right - self.left
        self.font_size = np.mean(font_sizes)
        self.numbers_quantity = len(list(filter(lambda x: x.isdigit(), self.text_content)))
        self.numbers_percentage = self.numbers_quantity / self.text_len if self.text_len > 0 else 0
        self.bold = self.bold_tag_number / len(self.segment_tags)
        self.italics = self.italics_tag_number / len(self.segment_tags)
        self.starts_upper = self.text_content[0].isupper()
        self.starts_number = self.text_content[0].isdigit()
        self.starts_number_bar = len(re.findall(r"^[0-9]\/", self.text_content)) == 1
        self.starts_letter_dot = len(re.findall(r"^[a-zA-Z]\.", self.text_content)) == 1
        self.uppercase = self.text_content.upper() == self.text_content

        first_characters = self.text_content.split(" ")[0].split("\n")[0].split("\t")[0]

        special_markers = [".", "(", ")", "\\", "/", ":", ";", "-", "_", "[", "]", "•", "◦", "*"]
        clean_first_characters = [x for x in first_characters if x not in special_markers]

        characters_checker = {
            1: lambda x_list: len(x_list) == len([letter for letter in x_list if letter in "IVXLCDM"]),
            2: lambda x_list: len(x_list) == len([letter for letter in x_list if letter in "IVXLCDM".lower()]),
            3: lambda x_list: len(x_list) == len([letter for letter in x_list if letter in "1234567890"]),
            4: lambda x_list: len(x_list) == len([letter for letter in x_list if letter == letter.upper()]),
        }

        self.first_characters_type = 0
        for index, type_checker in characters_checker.items():
            if type_checker(clean_first_characters):
                self.first_characters_type = index
                break

        self.bullet_points_type = (
            special_markers.index(first_characters[-1]) + 1 if first_characters[-1] in special_markers else 0
        )

        self.first_characters_special_markers_count = len([x for x in first_characters[:-1] if x in special_markers])

        self.is_left = self.left < self.page_width - self.right
        self.indentation = int((self.left - self.modes.left_space_mode) / 15) if self.is_left else -1
        self.font_size_average = sum(self.font_sizes) / len(self.font_sizes)

        self.space_to_right_margin = self.page_width - self.right - self.modes.right_space_mode
        self.space_to_left_margin = self.left - self.modes.left_space_mode
        self.text_centered = 1 if abs(self.space_to_left_margin - self.space_to_right_margin) < 10 else 0

    def get_context_features(self):
        context = list()
        for i in range(4):
            if not self.context_segments[i]:
                context.extend([0] * 13)
                continue

            context.extend(
                [
                    self.context_segments[i].bold,
                    self.context_segments[i].italics,
                    self.context_segments[i].font_size / self.context_segments[i].font_size_average,
                    self.context_segments[i].line_height,
                    self.context_segments[i].numbers_quantity,
                    self.context_segments[i].dots_percentage,
                    1 if self.context_segments[i].uppercase else 0,
                    self.context_segments[i].text_centered,
                    self.context_segments[i].bullet_points_type,
                    self.context_segments[i].first_characters_type,
                    self.context_segments[i].first_characters_special_markers_count,
                    self.context_segments[i].is_left,
                    self.context_segments[i].indentation,
                ]
            )

        return context

    def get_features_array(self) -> np.array:
        return np.array(
            [
                self.bold,
                self.italics,
                self.font_size / self.font_size_average,
                self.line_height,
                self.numbers_quantity,
                self.dots_percentage,
                1 if self.uppercase else 0,
                self.text_centered,
                self.bullet_points_type,
                self.first_characters_type,
                self.first_characters_special_markers_count,
                self.is_left,
                self.indentation,
                self.title_index,
            ]
            + self.get_context_features()
        )

    def tag_after_last_tag(self, tag: PdfTag):
        if self.last_tag is None:
            return True

        if self.last_tag.bounding_box.bottom < tag.bounding_box.bottom:
            return True

        if self.last_tag.bounding_box.left < tag.bounding_box.left:
            return True

        return False

    @staticmethod
    def from_pdf_features(pdf_features: TocPdfFeatures) -> List["SegmentTwoModelsV3SegmentsContext2"]:
        segments: List["SegmentTwoModelsV3SegmentsContext2"] = list()
        title_index = 0
        modes = Modes(pdf_features)
        for index, pdf_segment in enumerate(pdf_features.pdf_segments):
            valid_tag_types = [TAG_TYPE_DICT["title"], TAG_TYPE_DICT["text"], TAG_TYPE_DICT["list"]]

            if pdf_segment.segment_type not in valid_tag_types:
                continue

            segment_landmarks = SegmentTwoModelsV3SegmentsContext2(index, pdf_segment, pdf_features, title_index, modes)

            if pdf_segment.segment_type == TAG_TYPE_DICT["title"]:
                title_index += 1

            segments.append(segment_landmarks)

        segments_sorted = sorted(segments, key=lambda x: (x.page_number, x.top))
        context_size = 2
        for index, segment in enumerate(segments_sorted):
            for j in range(1, context_size + 1):
                if index - j < 0:
                    segment.context_segments.append(None)
                    continue
                segment.context_segments.append(segments_sorted[index - j])

            for j in range(1, context_size + 1):
                if index + j >= len(segments_sorted):
                    segment.context_segments.append(None)
                    continue
                segment.context_segments.append(segments_sorted[index + j])

        return segments
