from bs4 import BeautifulSoup

from typing import List

from extract_pdf_paragraphs.PdfFeatures.PdfFont import PdfFont
from extract_pdf_paragraphs.PdfFeatures.PdfPage import PdfPage
from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag


class PdfFeatures:
    def __init__(
        self,
        pages: List[PdfPage],
        fonts: List[PdfFont],
        file_name="",
        file_type: str = "",
    ):
        self.pages = pages
        self.fonts = fonts
        self.file_name = file_name
        self.file_type = file_type

    @staticmethod
    def from_pdfalto(file_path) -> "PdfFeatures":
        with open(file_path, mode="r") as xml_file:
            xml_content = BeautifulSoup(xml_file.read(), "lxml-xml")

        return PdfFeatures.from_xml_content(xml_content)

    @staticmethod
    def from_xml_content(xml_content):
        pages = list()
        fonts = [PdfFont.from_text_style_pdfalto(xml_tag) for xml_tag in xml_content.find_all("TextStyle")]

        for xml_page in xml_content.find_all("Page"):
            pages.append(PdfPage.from_pdfalto(xml_page, fonts))

        return PdfFeatures(pages, fonts)

    @staticmethod
    def get_tags_from_pdf_features(pdf_features: "PdfFeatures") -> List[PdfTag]:
        pdf_tags: List[PdfTag] = list()
        for pdf_tag in pdf_features.get_tags():
            pdf_tags.append(pdf_tag)

        return pdf_tags

    def get_tags(self) -> List[PdfTag]:
        tags: List[PdfTag] = list()
        for page in self.pages:
            for tag in page.tags:
                tags.append(tag)
        return tags


if __name__ == "__main__":
    with open("/back/projects/pdf_paragraphs_extraction/src/test_files/test.xml", mode="r") as xml_file:
        xml_content = BeautifulSoup(xml_file.read(), "lxml-xml")

    PdfFeatures.from_xml_content(xml_content)
