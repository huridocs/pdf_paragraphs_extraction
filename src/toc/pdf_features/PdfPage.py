from bs4 import Tag


from src.toc.pdf_features.PdfIllustration import PdfIllustration

from src.toc.pdf_features.PdfFont import PdfFont

from src.toc.pdf_features.PdfTag import PdfTag


class PdfPage:
    def __init__(
        self, page_number: int, page_width: int, page_height: int, tags: list[PdfTag], illustrations: list[PdfIllustration]
    ):
        self.page_number = page_number
        self.page_width = page_width
        self.page_height = page_height
        self.tags = tags
        self.illustrations: list[PdfIllustration] = sorted(illustrations, key=lambda x: x.bounding_box.top)

    @staticmethod
    def from_pdfalto(xml_page: Tag, fonts: list[PdfFont]):
        xml_tags = [xml_tag for xml_tag in xml_page.find_all("TextLine")]
        tags = [PdfTag.from_pdfalto(xml_page["PHYSICAL_IMG_NR"], xml_tag, fonts) for xml_tag in xml_tags]
        tags = [x for x in tags if x.content != "" and x.font is not None]
        illustrations_tags = [tag for tag in xml_page.find_all("Illustration")]
        pdf_illustrations = [PdfIllustration.from_pdfalto(xml_page["PHYSICAL_IMG_NR"], tag) for tag in illustrations_tags]
        return PdfPage(
            int(xml_page["PHYSICAL_IMG_NR"]),
            int(float(xml_page["WIDTH"])),
            int(float(xml_page["HEIGHT"])),
            tags,
            pdf_illustrations,
        )
