from os.path import join
from pdf_features.PdfToken import PdfToken
from pdf_token_type_labels.PdfLabels import PdfLabels

from paragraph_extraction_trainer.Paragraph import Paragraph
from pdf_features.PdfFeatures import PdfFeatures
from paragraph_extraction_trainer.trainer_paths import PARAGRAPH_EXTRACTION_RELATIVE_PATH
from pdf_tokens_type_trainer.config import LABELS_FILE_NAME


class PdfParagraphTokens:
    def __init__(self, pdf_features: PdfFeatures, paragraphs: list[Paragraph]):
        self.pdf_features: PdfFeatures = pdf_features
        self.paragraphs = paragraphs

    @staticmethod
    def get_page_labels(paragraphs_extractions_labels: PdfLabels, page_number: int):
        page_labels = []

        for page in paragraphs_extractions_labels.pages:
            if page.number != page_number:
                continue

            for label_index, label in enumerate(sorted(page.labels, key=lambda _label: _label.area())):
                page_labels.append((label_index, label, page.number))

        return page_labels

    @staticmethod
    def from_labeled_data(pdf_labeled_data_root_path, dataset, pdf_name):
        pdf_features = PdfFeatures.from_labeled_data(pdf_labeled_data_root_path, dataset, pdf_name)
        paragraph_extraction_labeled_data_path = str(join(pdf_labeled_data_root_path, PARAGRAPH_EXTRACTION_RELATIVE_PATH))
        paragraph_extraction_labels_path = join(paragraph_extraction_labeled_data_path, dataset, pdf_name, LABELS_FILE_NAME)
        paragraphs_extractions_labels = PdfFeatures.load_labels(paragraph_extraction_labels_path)
        return PdfParagraphTokens.set_paragraphs(pdf_features, paragraphs_extractions_labels)

    @staticmethod
    def set_paragraphs(pdf_features: PdfFeatures, paragraphs_extractions_labels: PdfLabels):
        tokens_by_labels: dict[int, Paragraph] = dict()

        for token_index, (page, token) in enumerate(pdf_features.loop_tokens()):
            page_labels = PdfParagraphTokens.get_page_labels(paragraphs_extractions_labels, page.page_number)
            intersection, best_label = PdfParagraphTokens.get_intersected_label(page_labels, token)

            if intersection:
                tokens_by_labels.setdefault(best_label, Paragraph([])).add_token(token)
            else:
                tokens_by_labels[-token_index - 1] = Paragraph(tokens=[token])

        return PdfParagraphTokens(pdf_features, list(tokens_by_labels.values()))

    @staticmethod
    def get_intersected_label(page_labels, token):
        max_intersection = 0
        best_label = -1
        for label_index, label, label_page_number in page_labels:
            intersection = token.get_label_intersection_percentage(label)

            if intersection > max_intersection:
                max_intersection = intersection
                best_label = label_index

            if max_intersection > 99:
                break

        return max_intersection, best_label

    def get_paragraph_for_token(self, token: PdfToken):
        for paragraph in self.paragraphs:
            if token in paragraph.tokens:
                return paragraph

    def check_same_paragraph(self, token_1: PdfToken, token_2: PdfToken):
        return self.get_paragraph_for_token(token_1) == self.get_paragraph_for_token(token_2)
