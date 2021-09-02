from collections import defaultdict, namedtuple
from typing import Dict, List

from bs4 import Tag

PageInfo = namedtuple('PageInfo', ['page_number', 'height', 'width', 'fonts', 'images'])


def get_tags_by_page_pdfalto(xml) -> Dict[PageInfo, List[Tag]]:
    tags_by_page = defaultdict(list)
    fonts = xml.find_all('TextStyle')
    for xml_page in xml.find_all('Page'):
        images = xml_page.find_all('Illustration')
        page_number = int(xml_page['PHYSICAL_IMG_NR'])
        page_info = PageInfo(page_number=page_number,
                             height=float(xml_page['HEIGHT']),
                             width=float(xml_page['WIDTH']),
                             fonts=frozenset(fonts),
                             images=frozenset(images))

        page_text_lines = remove_empty_text_lines(xml_page)
        tags_by_page[page_info] = page_text_lines

    return tags_by_page


def remove_empty_text_lines(xml_page):
    page_text_lines = list()
    for text_line in xml_page.find_all('TextLine'):
        if len(list(text_line.find_all('String'))) == 0:
            continue

        page_text_lines.append(text_line)

    return page_text_lines
