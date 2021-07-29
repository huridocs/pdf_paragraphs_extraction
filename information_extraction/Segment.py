import re
from typing import List
import numpy as np

from information_extraction.SegmentTag import SegmentTag
from pdfalto.PDFFeatures import PDFFeatures


class Segment(object):
    def __init__(self, segment_tags: List[SegmentTag], pdf_features: PDFFeatures, page_number: int):
        self.ml_class_label: int = 0
        self.confidence: float = 0
        self.page_number = page_number
        self.segment_tags = segment_tags
        self.pdf_features = pdf_features
        self.images = pdf_features.page_images[page_number]
        self.page_width = self.pdf_features.page_width
        self.page_height = self.pdf_features.page_height
        self.text_content: str = ''
        self.text_len: int = 0
        self.top: float = 0
        self.left: float = 0
        self.right: float = 0
        self.bottom: float = 0
        self.height: float = 0
        self.width: float = 0
        self.font_size: float = 0.0
        self.font_family: str = ''
        self.font_color: str = ''
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
        self.last_tag: SegmentTag = None
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
        self.distance_to_last_image: float = 0
        self.last_image_height: float = 0
        self.set_features()

    def initialize_features(self):
        self.page_width = self.pdf_features.page_width
        self.page_height = self.pdf_features.page_height
        self.ml_class_label: int = 0
        self.text_content: str = ''
        self.text_len: int = 0
        self.top: float = 0
        self.left: float = 0
        self.right: float = 0
        self.bottom: float = 0
        self.height: float = 0
        self.width: float = 0
        self.font_size: float = 0.0
        self.font_family: str = ''
        self.font_color: str = ''
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
        self.last_tag: SegmentTag = None
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
        self.distance_to_last_image: float = 0
        self.last_image_height: float = 0

    def set_features(self):
        self.initialize_features()
        self.font_family = self.segment_tags[0].font.family
        self.font_color = self.segment_tags[0].font.color
        self.line_height = self.segment_tags[0].height
        self.top = self.segment_tags[0].top
        self.left = self.segment_tags[0].left
        self.right = self.segment_tags[0].left + self.segment_tags[0].width
        self.bottom = self.segment_tags[0].top + self.segment_tags[0].height
        words: List[str] = list()

        font_sizes = list()
        for tag in self.segment_tags:
            words.extend(tag.text.split())
            self.top = min(self.top, tag.top)
            self.left = min(self.left, tag.left)
            self.right = max(self.right, tag.left + tag.width)
            self.bottom = max(self.bottom, tag.top + tag.height)
            self.bold_tag_number = self.bold_tag_number + 1 if tag.font.bold else self.bold_tag_number
            self.italics_tag_number = self.italics_tag_number + 1 if tag.font.italics else self.italics_tag_number
            font_sizes.append(tag.font.size)
            if self.tag_after_last_tag(tag):
                self.last_tag = tag

        self.top = self.top / self.page_height
        self.bottom = self.bottom / self.page_height
        self.right = self.right / self.page_width
        self.left = self.left / self.page_width

        if len(list(self.images)) > 0:
            positions = [float(image['VPOS']) + float(image['HEIGHT']) for image in list(self.images)]
            self.last_image_height = max(positions) / self.page_height
            self.distance_to_last_image = self.last_image_height - self.top

        self.text_content = ' '.join(words)
        self.text_len = len(self.text_content)
        self.dots_percentage = self.text_content.count('.') / self.text_len if self.text_len > 0 else 0
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
        first_characters = self.text_content.split(' ')[0].split('.')[0]
        roman_numbers = ''.join(filter(lambda x: x in 'IVXLCDM', first_characters))
        if len(roman_numbers) > 0 and roman_numbers == first_characters:
            self.starts_with_roman_numbers = True
        self.starts_with_square_brackets = self.text_content[0] == '['

    def get_features_array(self) -> np.array:
        return np.array([
            self.pdf_features.font_size_mode,
            self.pdf_features.lines_space_mode,
            self.pdf_features.font_family_mode_normalized,
            self.pdf_features.page_width / 5000,
            self.pdf_features.page_height / 5000,
            self.pdf_features.left_space_mode / self.page_width,
            self.bold,
            self.italics,
            self.text_len,
            self.top,
            self.bottom,
            self.height,
            self.width,
            self.font_size / self.pdf_features.font_size_mode,
            self.line_height,
            self.numbers_percentage,
            1 if self.starts_upper else 0,
            1 if self.starts_number else 0,
            self.starts_number_bar,
            self.numbers_quantity,
            self.starts_with_square_brackets,
            self.starts_letter_dot,
            self.dots_percentage,
            self.distance_to_last_image,
            self.last_image_height,
            1 if self.uppercase else 0
        ])

    def is_selected(self, box_left, box_top, box_right, box_bottom):
        left = self.left * self.page_width
        right = self.right * self.page_width
        top = self.top * self.page_height
        bottom = self.bottom * self.page_height

        if box_bottom < top or bottom < box_top:
            return False

        if box_right < left or right < box_left:
            return False

        return True

    def __iter__(self):
        for attr, value in self.__dict__.items():
            if attr == 'tags':
                value = list(map(lambda x: str(x.tag), value))
            yield attr, value

    def tag_after_last_tag(self, tag: SegmentTag):
        if self.last_tag is None:
            return True

        if self.last_tag.bottom < tag.bottom:
            return True

        if self.last_tag.left < tag.left:
            return True

        return False

    def load_prediction(self):
        for tag in self.segment_tags:
            if tag.ml_class_label != 0:
                self.ml_class_label = tag.ml_class_label
                break

    def remove_tag(self, segment_tag: SegmentTag):
        self.segment_tags.remove(segment_tag)
        if len(self.segment_tags) == 0:
            self.initialize_features()
            return
        self.set_features()

    def add_tag(self, segment_tag: SegmentTag):
        self.segment_tags.append(segment_tag)
        self.set_features()

    def merge_segment(self, segment_to_merge: 'Segment'):
        tags = self.segment_tags
        tags.extend(segment_to_merge.segment_tags)
        self.initialize_features()
        self.set_features()
        return self
