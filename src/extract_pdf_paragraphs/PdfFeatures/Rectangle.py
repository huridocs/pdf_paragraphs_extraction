import math
from typing import List, Dict
from bs4 import Tag


class Rectangle:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    @staticmethod
    def from_tag(tag: Tag) -> "Rectangle":
        x_min = int(float(tag["HPOS"])) if not math.isnan(float(tag["HPOS"])) else 0
        y_min = int(float(tag["VPOS"])) if not math.isnan(float(tag["VPOS"])) else 0
        x_max = int(float(tag["WIDTH"])) + x_min if not math.isnan(float(tag["WIDTH"])) else x_min
        y_max = int(float(tag["HEIGHT"])) + y_min if not math.isnan(float(tag["HEIGHT"])) else y_min

        return Rectangle(x_min, y_min, x_max, y_max)

    @staticmethod
    def from_segment_dict(paragraph: Dict[str, any]) -> "Rectangle":
        return Rectangle(
            paragraph["left"],
            paragraph["top"],
            paragraph["left"] + paragraph["width"],
            paragraph["top"] + paragraph["height"],
        )

    @staticmethod
    def merge_rectangles(rectangles: List["Rectangle"]) -> "Rectangle":
        left = min([rectangle.left for rectangle in rectangles])
        top = min([rectangle.top for rectangle in rectangles])
        right = max([rectangle.right for rectangle in rectangles])
        bottom = max([rectangle.bottom for rectangle in rectangles])

        return Rectangle(left, top, right, bottom)

    @staticmethod
    def from_tags(tags: List[Tag]) -> "Rectangle":
        return Rectangle.merge_rectangles([Rectangle.from_tag(tag) for tag in tags])

    @staticmethod
    def from_pdftags(tags) -> "Rectangle":
        return Rectangle.merge_rectangles(
            [
                Rectangle(
                    tag.bounding_box.left,
                    tag.bounding_box.top,
                    tag.bounding_box.right,
                    tag.bounding_box.bottom,
                )
                for tag in tags
            ]
        )

    @staticmethod
    def is_inside_tag(big_rectangle: "Rectangle", small_rectangle: "Rectangle") -> bool:
        if big_rectangle.left > small_rectangle.right:
            return False
        elif big_rectangle.right < small_rectangle.left:
            return False
        elif big_rectangle.bottom < small_rectangle.top:
            return False
        elif big_rectangle.top > small_rectangle.bottom:
            return False

        return True

    @staticmethod
    def from_segment_box(segment_box: "SegmentBox"):
        return Rectangle(
            segment_box.left, segment_box.top, segment_box.left + segment_box.width, segment_box.top + segment_box.height
        )
