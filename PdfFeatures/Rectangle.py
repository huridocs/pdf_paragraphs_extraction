import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from typing import List
from bs4 import Tag


class Rectangle():
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    @staticmethod
    def from_tag(tag: Tag) -> 'Rectangle':
        x_min = int(float(tag['HPOS']))
        y_min = int(float(tag['VPOS']))
        x_max = int(float(tag['WIDTH'])) + x_min
        y_max = int(float(tag['HEIGHT'])) + y_min

        return Rectangle(x_min, y_min, x_max, y_max)


    @staticmethod
    def merge_rectangles(rectangles: List['Rectangle']) -> 'Rectangle':

        left = min([rectangle.left for rectangle in rectangles])
        top = min([rectangle.top for rectangle in rectangles])
        right = max([rectangle.right for rectangle in rectangles])
        bottom = max([rectangle.bottom for rectangle in rectangles])

        return Rectangle(left, top, right, bottom)

    @staticmethod
    def from_tags(tags: List[Tag]) -> 'Rectangle':

        return Rectangle.merge_rectangles([Rectangle.from_tag(tag) for tag in tags])

    @staticmethod
    def from_pdftags(tags) -> 'Rectangle':

        return Rectangle.merge_rectangles([Rectangle(tag.bounding_box.left, tag.bounding_box.top,
                       tag.bounding_box.right, tag.bounding_box.bottom) for tag in tags])

    @staticmethod
    def is_inside_tag(big_rectangle: 'Rectangle', small_rectangle: 'Rectangle') -> bool:

        if big_rectangle.left > small_rectangle.right:
            return False
        elif big_rectangle.right < small_rectangle.left:
            return False
        elif big_rectangle.bottom < small_rectangle.top:
            return False
        elif big_rectangle.top > small_rectangle.bottom:
            return False

        return True
