from bs4 import Tag


class PdfFont:
    def __init__(self, font_id: str, bold: bool, italics: bool, font_size: float, color: str):
        self.color = color
        self.font_size = font_size
        self.font_id = font_id
        self.bold: bool = bold
        self.italics: bool = italics

    @staticmethod
    def from_text_style_pdfalto(xml_text_style_tag: Tag):
        bold: bool = "bold" in xml_text_style_tag["FONTSTYLE"] if "FONTSTYLE" in xml_text_style_tag.attrs else False
        italics: bool = "italics" in xml_text_style_tag["FONTSTYLE"] if "FONTSTYLE" in xml_text_style_tag.attrs else False
        font_size = float(xml_text_style_tag["FONTSIZE"])
        color = xml_text_style_tag["FONTCOLOR"]
        return PdfFont(xml_text_style_tag["ID"], bold, italics, font_size, color)
