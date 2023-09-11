from os.path import join
from pdf_features.PdfToken import PdfToken
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from extract_pdf_paragraphs.Paragraph import Paragraph
from pdf_features.PdfFeatures import PdfFeatures
from config import PARAGRAPH_EXTRACTION_LABELED_DATA_PATH, PDF_LABELED_DATA_ROOT_PATH
from pdf_tokens_type_trainer.config import LABELS_FILE_NAME


class PdfParagraphTokens:
    def __init__(self, pdf_features: PdfFeatures, paragraphs: list[Paragraph]):
        self.pdf_features: PdfFeatures = pdf_features
        self.paragraphs = paragraphs

    @staticmethod
    def loop_labels(paragraphs_extractions_labels):
        label_index = 0
        for page in paragraphs_extractions_labels.pages:
            for label in page.labels:
                yield label_index, label, page.number
                label_index += 1

    @staticmethod
    def from_labeled_data(dataset, pdf_name):
        pdf_features = PdfFeatures.from_labeled_data(PDF_LABELED_DATA_ROOT_PATH, dataset, pdf_name)
        paragraph_extraction_labels_path = join(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH, dataset, pdf_name, LABELS_FILE_NAME)
        paragraphs_extractions_labels = PdfFeatures.load_token_type_labels(paragraph_extraction_labels_path)
        return PdfParagraphTokens.set_paragraphs(pdf_features, paragraphs_extractions_labels)

    @staticmethod
    def set_paragraphs(pdf_features: PdfFeatures, paragraphs_extractions_labels: TokenTypeLabels):
        tokens_by_labels: dict[int, Paragraph] = {
            -token_index - 1: Paragraph([token]) for token_index, (page, token) in enumerate(pdf_features.loop_tokens())
        }
        for label_index, label, label_page_number in PdfParagraphTokens.loop_labels(paragraphs_extractions_labels):
            for token_index, (page, token) in enumerate(pdf_features.loop_tokens()):
                if label_page_number != page.page_number or -token_index - 1 not in tokens_by_labels:
                    continue
                if token.inside_label(label):
                    tokens_by_labels.setdefault(label_index, Paragraph([])).add_token(token)
                    del tokens_by_labels[-token_index - 1]

        return PdfParagraphTokens(pdf_features, list(tokens_by_labels.values()))

    def get_paragraph_for_token(self, token: PdfToken):
        for paragraph in self.paragraphs:
            if token in paragraph.tokens:
                return paragraph

    def check_same_paragraph(self, token_1: PdfToken, token_2: PdfToken):
        return self.get_paragraph_for_token(token_1) == self.get_paragraph_for_token(token_2)


#
# if __name__ == "__main__":
#     paragraph_tokens = PdfParagraphTokens.from_labeled_data("one_column_train", "cejil_staging1")
#     for paragraph in paragraph_tokens.paragraphs:
#         print([token.id for token in paragraph.tokens])
