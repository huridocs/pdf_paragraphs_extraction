import numpy as np

from copy import deepcopy

from pdf_features.PdfFeatures import PdfFeatures
from pdf_features.PdfFont import PdfFont
from pdf_features.PdfSegment import PdfSegment
from pdf_features.PdfToken import PdfToken
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.TokenType import TokenType

from extract_pdf_paragraphs.segmentator.get_features import PdfAltoXml


class LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features:
    def __init__(self, X_train, y_train, model_configs: dict, model=None):
        self.X_train = X_train
        self.y_train = y_train
        self.model_configs = model_configs
        self.model = model

    @staticmethod
    def __get_training_data(pdf_features: PdfFeatures, model_configs: dict):
        X = None
        y = np.array([])
        context_size: int = model_configs["context_size"]
        pdfalto_xml = PdfAltoXml(pdf_features)

        for _page in pdf_features.pages:
            page = deepcopy(_page)

            for i in range(context_size):
                page.tokens.insert(
                    0,
                    PdfToken(
                        page.page_number,
                        "pad_tag",
                        "",
                        PdfFont("pad_font_id", False, False, 0.0),
                        -i - 1,
                        -i - 1,
                        Rectangle(0, 0, 0, 0),
                        TokenType.TEXT
                    ),
                )

            for i in range(context_size):
                page.tokens.append(
                    PdfToken(
                        page.page_number,
                        "pad_tag",
                        "",
                        PdfFont("pad_font_id", False, False, 0.0),
                        -i - 1000,
                        -i - 1000,
                        Rectangle(0, 0, 0, 0),
                        TokenType.TEXT
                    )
                )

            for tag_index, tag in enumerate(page.tokens):
                if tag_index + (2 * context_size + 2) > len(page.tokens):
                    continue

                new_data_row = []

                for i in range(2 * context_size + 1):
                    new_data_row.extend(
                        pdfalto_xml.get_features_for_given_tags(
                            page.tokens[tag_index + i], page.tokens[tag_index + i + 1], page.tokens
                        )
                    )

                X = np.array([new_data_row]) if X is None else np.concatenate((X, np.array([new_data_row])), axis=0)

                if page.tokens[tag_index + context_size].segment_no == page.tokens[tag_index + context_size + 1].segment_no:
                    y = np.append(y, 1)
                else:
                    y = np.append(y, 0)

        return X, y

    @staticmethod
    def get_feature_matrix(pdf_features_list: list[PdfFeatures], model_configs: dict):
        X_train = None
        y_train = np.array([])

        for pdf_features in pdf_features_list:
            X_sub, y_sub = LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features.__get_training_data(
                pdf_features, model_configs
            )
            if X_sub is None:
                print(f"File has no data")
                continue
            X_train = X_sub if X_train is None else np.concatenate((X_train, X_sub), axis=0)
            y_train = np.append(y_train, y_sub)

        return LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features(X_train, y_train, model_configs)

    def get_predicted_segments(self, pdfalto_xml, page_tags: list[PdfToken]) -> list[PdfSegment]:
        X = np.array([])
        context_size: int = self.model_configs["context_size"]

        for i in range(context_size):
            page_tags.insert(
                0,
                PdfToken(
                    page_tags[0].page_number,
                    "pad_tag",
                    "",
                    PdfFont("pad_font_id", False, False, 0.0),
                    -i - 1,
                    -i - 1,
                    Rectangle(0, 0, 0, 0),
                    TokenType.TEXT,
                ),
            )

        for i in range(context_size):
            page_tags.append(
                PdfToken(
                    page_tags[0].page_number,
                    "pad_tag",
                    "",
                    PdfFont("pad_font_id", False, False, 0.0),
                    -i - 1000,
                    -i - 1000,
                    Rectangle(0, 0, 0, 0),
                    TokenType.TEXT
                )
            )

        for tag_index, tag in enumerate(page_tags):
            if tag_index + (2 * context_size + 2) > len(page_tags):
                continue

            new_data_row = []

            for i in range(2 * context_size + 1):
                new_data_row.extend(
                    pdfalto_xml.get_features_for_given_tags(
                        page_tags[tag_index + i], page_tags[tag_index + i + 1], page_tags
                    )
                )

            if len(new_data_row) == 0:
                print(pdfalto_xml.pdf_features.file_name, " - ", str(page_tags[0].page_number))
            X = np.array([new_data_row]) if len(X) == 0 else np.concatenate((X, np.array([new_data_row])), axis=0)

        y = self.model.predict(X) if len(X.shape) == 2 else self.model.predict([X])
        same_paragraph_prediction = [True if prediction > 0.5 else False for prediction in y]

        segments_by_tokens = list()
        segments_by_tokens.append([page_tags[context_size]])
        for prediction_index, same_paragraph in enumerate(same_paragraph_prediction):
            if same_paragraph:
                segments_by_tokens[-1].append(page_tags[prediction_index + context_size + 1])
                continue

            segments_by_tokens.append([page_tags[prediction_index + context_size + 1]])

        pdf_segments_for_page: list[PdfSegment] = [PdfSegment.from_pdf_tokens(pdf_tokens) for pdf_tokens in
                                                   segments_by_tokens]

        return pdf_segments_for_page

    def predict(self, pdf_features: PdfFeatures) -> list[PdfSegment]:
        pdfalto_xml = PdfAltoXml(pdf_features)

        segments: list[PdfSegment] = list()
        for page in pdf_features.pages:
            if len(page.tokens) == 0 or len(page.tokens) == 1:
                continue
            segments_for_a_page: list[PdfSegment] = self.get_predicted_segments(pdfalto_xml, deepcopy(page.tokens))
            segments.extend(segments_for_a_page)

        return segments

    def get_segments_for_page(self, pdfalto_xml: PdfAltoXml, page_tags: list[PdfToken]) -> list[PdfSegment]:
        return self.get_predicted_segments(pdfalto_xml, deepcopy(page_tags))
