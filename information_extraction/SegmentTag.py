import bs4
import numpy as np

ML_CLASS_LABEL_PROPERTY = 'MLCLASSLABEL'
GROUP = 'GROUP'


class SegmentTag:
    def __init__(self, tag_xml: bs4.Tag, page_width: float, page_height: float, page_number: int, fonts=None):
        self.page_number: int = page_number
        self.tag = tag_xml
        self.page_width = page_width
        self.page_height = page_height

        self.top = float(self.tag['VPOS'])
        self.left = float(self.tag['HPOS'])
        self.width = float(self.tag['WIDTH'])
        self.height = float(self.tag['HEIGHT'])
        self.right = self.left + self.width
        self.bottom = self.top + self.height

        try:
            self.ml_class_label: int = int(self.tag[ML_CLASS_LABEL_PROPERTY])
        except KeyError:
            self.ml_class_label: int = 0

        self.font = []
        self.text = ''

        if len(tag_xml.find_all('String')) > 0:
            font_id = tag_xml.find_all('String')[0]['STYLEREFS']
            self.font = list(filter(lambda font: font.id == font_id, fonts))[0]

            self.text = ' '.join([string_tag['CONTENT'] for string_tag in tag_xml.find_all('String')])

    def get_features(self):
        x1 = self.left
        y1 = self.top
        width = self.width
        height = self.height

        x4 = (x1 + width)
        y4 = (y1 + height)

        result = np.array([x1, y1, x4, y4])
        return result

    def get_id(self):
        return f'{self.left}_{self.top}'

    def __eq__(self, other):
        return (self.page_number, self.left, self.top, self.height, self.width) == (
        other.page_number, other.left, other.top, other.height, other.width)

    def __hash__(self):
        return hash((self.page_number, self.left, self.top, self.height, self.width))