from pathlib import Path

import numpy as np
from extract_pdf_paragraphs.PdfSegment import PdfSegment
from pdf_features.PdfToken import PdfToken
from pdf_token_type_labels.TokenType import TokenType
from pdf_tokens_type_trainer.TokenFeatures import TokenFeatures
from pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer
from tqdm import tqdm


class ParagraphExtractorTrainer(TokenTypeTrainer):
    def loop_pages(self):
        for pdf_features in tqdm(self.pdfs_features):
            token_features = TokenFeatures(pdf_features)

            for page in pdf_features.pages:
                if len(page.tokens) < 2:
                    continue

                yield token_features, page

    def get_model_input(self):
        features_rows = []
        y = np.array([])

        contex_size = self.model_configuration.context_size
        for token_features, page in self.loop_pages():
            page_tokens = [
                self.get_padding_token(segment_number=i - 999999, page_number=page.page_number) for i in range(contex_size)
            ]
            page_tokens += page.tokens
            page_tokens += [
                self.get_padding_token(segment_number=999999 + i, page_number=page.page_number) for i in range(contex_size)
            ]

            tokens_indexes = range(contex_size, len(page_tokens) - contex_size)
            page_features = [self.get_context_features(token_features, page_tokens, i) for i in tokens_indexes]
            features_rows.extend(page_features)

            y = np.append(y, [int(page_tokens[i].segment_no == page_tokens[i + 1].segment_no) for i in tokens_indexes])

        return self.features_rows_to_x(features_rows), y

    def get_context_features(self, token_features: TokenFeatures, page_tokens: list[PdfToken], token_index: int):
        token_row_features = list()
        first_token_from_context = token_index - self.model_configuration.context_size
        for i in range(self.model_configuration.context_size * 2):
            first_token = page_tokens[first_token_from_context + i]
            second_token = page_tokens[first_token_from_context + i + 1]
            features = token_features.get_features(first_token, second_token, page_tokens)
            features += self.get_paragraph_extraction_features(first_token, second_token)
            token_row_features.extend(features)

        return token_row_features

    @staticmethod
    def get_paragraph_extraction_features(first_token: PdfToken, second_token: PdfToken) -> list[int]:
        one_hot_token_type_1 = [1 if token_type == first_token.token_type else 0 for token_type in TokenType]
        one_hot_token_type_2 = [1 if token_type == second_token.token_type else 0 for token_type in TokenType]
        return one_hot_token_type_1 + one_hot_token_type_2

    def loop_token_next_token(self):
        for pdf_features in self.pdfs_features:
            for page in pdf_features.pages:
                if not page.tokens:
                    continue

                if len(page.tokens) == 1:
                    yield page.tokens[0], page.tokens[0]

                for token, next_token in zip(page.tokens, page.tokens[1:]):
                    yield token, next_token

    def get_pdf_segments(self, paragraph_extractor_model_path: str | Path) -> list[PdfSegment]:
        self.predict(paragraph_extractor_model_path)
        pdf_segments: list[PdfSegment] = list()
        segment_tokens: list[PdfToken] = list()
        for token, next_token in self.loop_token_next_token():
            if token == next_token:
                pdf_segments.append(PdfSegment.from_pdf_tokens(segment_tokens))
                segment_tokens = []
                continue

            if not segment_tokens:
                segment_tokens.append(token)

            if not token.prediction:
                pdf_segments.append(PdfSegment.from_pdf_tokens(segment_tokens))
                segment_tokens = [next_token]
                continue

            segment_tokens.append(next_token)

        return pdf_segments

    def predict(self, model_path: str | Path = None):
        token_type_trainer = TokenTypeTrainer(self.pdfs_features)
        token_type_trainer.set_token_types()
        super().predict(model_path)
