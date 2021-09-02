from typing import List

from bs4 import Tag


class Font:
    def __init__(self, xml_style: Tag):
        #<TextStyle FONTCOLOR="000000" FONTFAMILY="verdana,bold" FONTSIZE="9.960" FONTSTYLE="bold" FONTTYPE="sans-serif" FONTWIDTH="proportional" ID="font0"/>
        self.id: str = xml_style['ID']
        self.size: int = int(float(xml_style['FONTSIZE']))
        self.family: str = xml_style['FONTFAMILY'].split(',')[0]
        self.color: str = xml_style['FONTCOLOR']
        self.bold: bool = 'bold' in xml_style['FONTSTYLE'] if 'FONTSTYLE' in xml_style.attrs else False
        self.italics: bool = 'italics' in xml_style['FONTSTYLE'] if 'FONTSTYLE' in xml_style.attrs else False

    @staticmethod
    def from_page_xml_tag(xml_tags: List[Tag]):
        fonts: List[Font] = list()
        for xml_tag in xml_tags:
            fonts.append(Font(xml_tag))
        return fonts
