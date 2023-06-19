from bs4 import BeautifulSoup


from extract_pdf_paragraphs.pdf_features.PdfFont import PdfFont
from extract_pdf_paragraphs.pdf_features.PdfPage import PdfPage
from extract_pdf_paragraphs.pdf_features.PdfTag import PdfTag


class PdfFeatures:
    def __init__(
        self,
        pages: list[PdfPage],
        fonts: list[PdfFont],
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
    def get_tags_from_pdf_features(pdf_features: "PdfFeatures") -> list[PdfTag]:
        pdf_tags: list[PdfTag] = list()
        for pdf_tag in pdf_features.get_tags():
            pdf_tags.append(pdf_tag)

        return pdf_tags

    def get_tags(self) -> list[PdfTag]:
        tags: list[PdfTag] = list()
        for page in self.pages:
            for tag in page.tags:
                tags.append(tag)
        return tags


if __name__ == "__main__":
    with open("test.xml", mode="r") as xml_file:
        xml_content = BeautifulSoup(xml_file.read(), "lxml-xml")

    PdfFeatures.from_xml_content(xml_content)
