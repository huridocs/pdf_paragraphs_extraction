from collections import Counter
from typing import List, Dict

from extract_pdf_paragraphs.pdf_features.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.pdf_features.PdfTag import PdfTag


class PdfAltoXml:
    def __init__(self, pdf_features: PdfFeatures):
        self.pdf_features = pdf_features
        self.tag_types: Dict[str, str] = {tag.id: tag.tag_type for page in pdf_features.pages for tag in page.tags}
        self.tag_types["pad_tag"] = "pad_type"
        self.lines_space_mode: float = 0
        self.right_space_mode: float = 0
        self.font_size_mode: float = 0

        self.get_modes()
        self.get_mode_font()

    def get_modes(self):
        self.get_left_right_block()
        line_spaces, right_spaces, left_spaces = [0], [0], [0]

        for page in self.pdf_features.pages:
            for tag in page.tags:
                top, height = tag.bounding_box.top, tag.bounding_box.height
                left, width = tag.bounding_box.left, tag.bounding_box.width
                bottom, right = tag.bounding_box.bottom, tag.bounding_box.right

                on_the_bottom = list(filter(lambda x: bottom < x.bounding_box.top, page.tags))

                if len(on_the_bottom) > 0:
                    line_spaces.append(min(map(lambda x: int(x.bounding_box.top - bottom), on_the_bottom)))

                same_line_tags = filter(
                    lambda x: (top <= x.bounding_box.top < bottom) or (top < x.bounding_box.bottom <= bottom), page.tags
                )
                on_the_right = filter(lambda x: right < x.bounding_box.left, same_line_tags)
                on_the_left = filter(lambda x: x.bounding_box.left < left, same_line_tags)

                if len(list(on_the_right)) == 0:
                    right_spaces.append(int(right))

                if len(list(on_the_left)) == 0:
                    left_spaces.append(int(left))

        self.lines_space_mode = max(set(line_spaces), key=line_spaces.count)
        self.right_space_mode = int(self.pdf_features.pages[0].page_width - max(set(right_spaces), key=right_spaces.count))

    def get_mode_font(self):
        fonts_counter: Counter = Counter()
        for page in self.pdf_features.pages:
            for tag in page.tags:
                fonts_counter.update([tag.font.font_id])

        if len(fonts_counter.most_common()) == 0:
            return

        font_mode_id = fonts_counter.most_common()[0][0]
        font_mode_tag = list(filter(lambda x: x.font_id == font_mode_id, self.pdf_features.fonts))
        if len(font_mode_tag) == 1:
            self.font_size_mode: float = float(font_mode_tag[0].font_size)

    def __get_features_for_next_tag(
        self, tags_for_page: List[PdfTag], previous_tag: PdfTag, next_tag: PdfTag, on_the_right_right_1, on_the_left_left_1
    ):
        top = next_tag.bounding_box.top
        left = next_tag.bounding_box.left
        right = next_tag.bounding_box.right
        height = next_tag.bounding_box.height
        width = next_tag.bounding_box.width

        on_the_right_left_2, on_the_right_right_2 = next_tag.on_the_right_left, next_tag.on_the_right_right
        on_the_left_left_2, on_the_left_right_2 = next_tag.on_the_left_left, next_tag.on_the_left_right
        left_gap_2 = left - on_the_left_right_2

        absolute_right_1 = max(previous_tag.bounding_box.left + previous_tag.bounding_box.width, on_the_right_right_1)
        absolute_right_2 = max(left + width, on_the_right_right_2)

        end_lines_difference = abs(absolute_right_1 - absolute_right_2)

        on_the_left_left_1 = previous_tag.bounding_box.left if on_the_left_left_1 == 0 else on_the_left_left_1
        on_the_left_left_2 = left if on_the_left_left_2 == 0 else on_the_left_left_2
        absolute_left_1 = min(previous_tag.bounding_box.left, on_the_left_left_1)
        absolute_left_2 = min(left, on_the_left_left_2)

        start_lines_differences = absolute_left_1 - absolute_left_2

        tags_in_the_middle = list(
            filter(lambda x: previous_tag.bounding_box.bottom <= x.bounding_box.top < top, tags_for_page)
        )
        tags_in_the_middle_top = (
            max(map(lambda x: x.bounding_box.top, tags_in_the_middle)) if len(tags_in_the_middle) > 0 else 0
        )
        tags_in_the_middle_bottom = (
            min(map(lambda x: x.bounding_box.bottom, tags_in_the_middle)) if len(tags_in_the_middle) > 0 else 0
        )

        top_distance = top - previous_tag.bounding_box.top - previous_tag.bounding_box.height

        gap_middle_top = (
            tags_in_the_middle_top - previous_tag.bounding_box.top - previous_tag.bounding_box.height
            if tags_in_the_middle_top > 0
            else 0
        )
        gap_middle_bottom = top - tags_in_the_middle_bottom if tags_in_the_middle_bottom > 0 else 0

        top_distance_gaps = top_distance - (gap_middle_bottom - gap_middle_top)

        right_distance = left - previous_tag.bounding_box.left - previous_tag.bounding_box.width
        left_distance = previous_tag.bounding_box.left - left

        height_difference = previous_tag.bounding_box.height - height

        same_font = True if previous_tag.font.font_id == next_tag.font.font_id else False
        tag_type = self.tag_types[next_tag.id]

        features = [
            same_font,
            absolute_right_1,
            top,
            right,
            width,
            height,
            top_distance,
            top_distance - self.lines_space_mode,
            top_distance_gaps,
            self.lines_space_mode - top_distance_gaps,
            self.right_space_mode - absolute_right_1,
            top_distance - previous_tag.bounding_box.height,
            start_lines_differences,
            right_distance,
            left_distance,
            left_gap_2,
            height_difference,
            end_lines_difference,
            tag_type == "text",
            tag_type == "title",
            tag_type == "figure",
            tag_type == "table",
            tag_type == "list",
            tag_type == "footnote",
            tag_type == "formula",
        ]

        return features

    def get_features_for_given_tags(
        self, tags_for_page: List[PdfTag], current_tag: PdfTag, tag_first: PdfTag, tag_second: PdfTag
    ) -> list[any]:
        on_the_right_left_1, on_the_right_right_1 = tag_first.on_the_right_left, tag_first.on_the_right_right
        on_the_left_left_1, on_the_left_right_1 = tag_first.on_the_left_left, tag_first.on_the_left_right

        right_gap_1 = on_the_right_left_1 - tag_first.bounding_box.right

        features = [
            self.font_size_mode / 100,
            current_tag.bounding_box.top,
            current_tag.bounding_box.right,
            current_tag.bounding_box.width,
            current_tag.bounding_box.height,
            right_gap_1,
            self.tag_types[current_tag.id] == "text",
            self.tag_types[current_tag.id] == "title",
            self.tag_types[current_tag.id] == "figure",
            self.tag_types[current_tag.id] == "table",
            self.tag_types[current_tag.id] == "list",
            self.tag_types[current_tag.id] == "footnote",
            self.tag_types[current_tag.id] == "formula",
        ]
        features.extend(
            self.__get_features_for_next_tag(tags_for_page, tag_first, tag_second, on_the_right_right_1, on_the_left_left_1)
        )

        on_the_right_left_1, on_the_right_right_1 = tag_second.on_the_right_left, tag_first.on_the_right_right
        on_the_left_left_1, on_the_left_right_1 = tag_second.on_the_left_left, tag_first.on_the_left_right

        features.extend(
            self.__get_features_for_next_tag(tags_for_page, tag_second, tag_first, on_the_right_right_1, on_the_left_left_1)
        )

        return features

    def get_left_right_block(self):
        for page in self.pdf_features.pages:
            for tag in page.tags:
                top = tag.bounding_box.top
                height = tag.bounding_box.height
                right = tag.bounding_box.right
                left = tag.bounding_box.left

                on_the_left = list(
                    filter(
                        lambda x: (top <= x.bounding_box.top < (top + height))
                        or (top < (x.bounding_box.bottom) <= (top + height)),
                        page.tags,
                    )
                )

                on_the_left = list(filter(lambda x: x.bounding_box.right < right, on_the_left))
                tag.on_the_left_left = 0 if len(on_the_left) == 0 else min(map(lambda x: x.bounding_box.left, on_the_left))
                tag.on_the_left_right = 0 if len(on_the_left) == 0 else max(map(lambda x: x.bounding_box.right, on_the_left))

                on_the_right = list(
                    filter(
                        lambda x: (top <= x.bounding_box.top < (top + height))
                        or (top < (x.bounding_box.bottom) <= (top + height)),
                        page.tags,
                    )
                )

                on_the_right = list(filter(lambda x: left < x.bounding_box.left, on_the_right))
                tag.on_the_right_left = (
                    0 if len(on_the_right) == 0 else min(map(lambda x: x.bounding_box.left, on_the_right))
                )
                tag.on_the_right_right = (
                    0 if len(on_the_right) == 0 else max(map(lambda x: x.bounding_box.right, on_the_right))
                )
