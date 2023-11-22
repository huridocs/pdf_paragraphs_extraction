from pdf_features.PdfPage import PdfPage
from pdf_features.Rectangle import Rectangle

from paragraph_extraction_trainer.Paragraph import Paragraph
from paragraph_extraction_trainer.PdfParagraphTokens import PdfParagraphTokens


class PredictionInfo:
    def __init__(self, pdf_paragraph_tokens: PdfParagraphTokens):
        self.pdf_paragraph_tokens = pdf_paragraph_tokens
        self.file_name = pdf_paragraph_tokens.pdf_features.file_name
        self.file_type = pdf_paragraph_tokens.pdf_features.file_type
        self.label_count = 0
        self.mistake_count = 0
        self.actual_paragraph_coordinates_by_page: dict[PdfPage, list[Rectangle]] = {}
        self.predicted_paragraph_coordinates_by_page: dict[PdfPage, list[Rectangle]] = {}
        self.find_actual_paragraphs_rectangles()
        self.find_predicted_paragraphs_rectangles()

    def find_actual_paragraphs_rectangles(self):
        for page in self.pdf_paragraph_tokens.pdf_features.pages:
            actual_paragraphs_for_page = [
                paragraph
                for paragraph in self.pdf_paragraph_tokens.paragraphs
                if paragraph.tokens[0].page_number == page.page_number
            ]
            self.actual_paragraph_coordinates_by_page[page] = []
            for paragraph in actual_paragraphs_for_page:
                paragraph_rectangle = Rectangle.merge_rectangles([token.bounding_box for token in paragraph.tokens])
                self.actual_paragraph_coordinates_by_page[page].append(paragraph_rectangle)

    def get_predicted_paragraph_coordinates_for_page(self, page: PdfPage, page_paragraphs: list[Paragraph]):
        if page_paragraphs:
            self.predicted_paragraph_coordinates_by_page[page] = []
            for paragraph in page_paragraphs:
                paragraph_rectangle = Rectangle.merge_rectangles([token.bounding_box for token in paragraph.tokens])
                self.predicted_paragraph_coordinates_by_page[page].append(paragraph_rectangle)

    def loop_token_next_token(self):
        for page in self.pdf_paragraph_tokens.pdf_features.pages:
            if not page.tokens:
                continue
            if len(page.tokens) == 1:
                yield page, page.tokens[0], page.tokens[0]
            for token, next_token in zip(page.tokens, page.tokens[1:]):
                yield page, token, next_token

    def find_predicted_paragraphs_rectangles(self):
        last_page = None
        for page, token, next_token in self.loop_token_next_token():
            if last_page != page:
                last_page = page
                self.predicted_paragraph_coordinates_by_page[page] = [token.bounding_box]
            if token == next_token:
                continue
            if token.prediction:
                current_paragraph_bounding_box = self.predicted_paragraph_coordinates_by_page[page][-1]
                updated_bounding_box = Rectangle.merge_rectangles([current_paragraph_bounding_box, next_token.bounding_box])
                self.predicted_paragraph_coordinates_by_page[page][-1] = updated_bounding_box
                continue
            self.predicted_paragraph_coordinates_by_page[page].append(next_token.bounding_box)
