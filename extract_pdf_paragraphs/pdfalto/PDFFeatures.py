import hashlib
from collections import Counter
from typing import Dict, List
import numpy as np

from bs4 import Tag

from extract_pdf_paragraphs.pdfalto.get_tags_by_page_pdfalto import PageInfo


class PDFFeatures:
    def __init__(self, tags_by_page: Dict[PageInfo, List[Tag]]):
        self.page_height = float(list(tags_by_page.keys())[0].height)
        self.page_width = float(list(tags_by_page.keys())[0].width)
        self.fonts = list(tags_by_page.keys())[0].fonts

        page_numbers = [x.page_number for x in tags_by_page.keys()]
        images = [x.images for x in tags_by_page.keys()]
        self.page_images = dict(zip(page_numbers, images))
        self.pages_tags: List[List[Tag]] = list(tags_by_page.values())

        self.lines_space_mode: float = 0
        self.right_space_mode: float = 0
        self.left_space_mode: float = 0
        self.font_size_mode: float = 0
        self.font_family_mode: int = 0
        self.font_family_mode_normalized: float = 0
        self.font_style_mode: int = 0
        self.id: int = 0
        self.fingerprint_vector: List[float] = []

        self.get_mode_font()
        self.get_modes()
        self.get_id()

    def get_modes(self):
        line_spaces, right_spaces, left_spaces = [0], [0], [0]

        for page_tags in self.pages_tags:
            for tag in page_tags:
                top, height = float(tag['VPOS']), float(tag['HEIGHT'])
                left, width = float(tag['HPOS']), float(tag['WIDTH'])
                bottom, right = top + height, left + width

                on_the_bottom = list(filter(lambda x: top + height < float(x['VPOS']), page_tags))

                if len(on_the_bottom) > 0:
                    line_spaces.append(min(map(lambda x: int(float(x['VPOS']) - bottom), on_the_bottom)))

                same_line_tags = filter(lambda x: (top <= float(x['VPOS']) < bottom) or
                                                  (top < (float(x['VPOS']) + float(x['HEIGHT'])) <= bottom), page_tags)
                on_the_right = filter(lambda x: right < float(x['HPOS']), same_line_tags)
                on_the_left = filter(lambda x: float(x['HPOS']) < left, same_line_tags)

                if len(list(on_the_right)) == 0:
                    right_spaces.append(int(right))

                if len(list(on_the_left)) == 0:
                    left_spaces.append(int(left))

        self.lines_space_mode = max(set(line_spaces), key=line_spaces.count)
        self.left_space_mode = max(set(left_spaces), key=left_spaces.count)
        self.right_space_mode = int(self.page_width - max(set(right_spaces), key=right_spaces.count))

    def get_mode_font(self):
        fonts_counter: Counter = Counter()
        for page_tags in self.pages_tags:
            for tag in page_tags:
                for string_tag in tag.find_all('String'):
                    fonts_counter.update([string_tag['STYLEREFS']])

        if len(fonts_counter.most_common()) == 0:
            return

        font_mode_id = fonts_counter.most_common()[0][0]
        font_mode_tag = list(filter(lambda x: x['ID'] == font_mode_id, self.fonts))
        if len(font_mode_tag) == 1:
            self.font_size_mode: float = float(font_mode_tag[0]['FONTSIZE'])
            font_family = str(font_mode_tag[0]['FONTFAMILY']).split(',')[0]
            font_family_mode: int = abs(int(str(hashlib.sha256(font_family.encode('utf-8')).hexdigest())[:8], 16))
            self.font_family_mode = font_family_mode
            self.font_family_mode_normalized = float(f'{str(font_family_mode)[0]}.{str(font_family_mode)[1:]}')

    def get_id(self):
        self.fingerprint_vector = [int(self.page_height),
                                   int(self.page_width),
                                   int(self.lines_space_mode),
                                   int(self.left_space_mode),
                                   self.font_size_mode,
                                   self.font_family_mode]

        self.id = np.linalg.norm(np.array(self.fingerprint_vector))
