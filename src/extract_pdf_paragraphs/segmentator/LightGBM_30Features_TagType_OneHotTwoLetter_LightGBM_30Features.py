import numpy as np
from typing import List, Dict
from pathlib import Path

from copy import deepcopy
from os import makedirs


import lightgbm as lgb

from extract_pdf_paragraphs.PdfFeatures.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.PdfFeatures.PdfFont import PdfFont
from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment
from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag
from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle
from extract_pdf_paragraphs.segmentator.get_features import PdfAltoXml


class LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features:

    def __init__(self, X_train, y_train, model_configs: Dict, model=None):
        self.X_train = X_train
        self.y_train = y_train
        self.model_configs = model_configs
        self.model = model

    @staticmethod
    def __get_training_data(pdf_features: PdfFeatures, model_configs: Dict):

        X = None
        y = np.array([])
        context_size: int = model_configs['context_size']
        pdfalto_xml = PdfAltoXml(pdf_features)

        for _page in pdf_features.pages:

            page = deepcopy(_page)

            for i in range(context_size):
                page.tags.insert(0, PdfTag(page.page_number, "pad_tag", "",
                                           PdfFont("pad_font_id", False, False, 0.0), -i-1, -i-1, Rectangle(0, 0, 0, 0), "pad_type"))

            for i in range(context_size):
                page.tags.append(PdfTag(page.page_number, "pad_tag", "",
                                           PdfFont("pad_font_id", False, False, 0.0), -i-1000, -i-1000, Rectangle(0, 0, 0, 0), "pad_type"))

            for tag_index, tag in enumerate(page.tags):
                if tag_index + (2*context_size+2) > len(page.tags):
                    continue

                new_data_row = []

                for i in range(2*context_size+1):
                    new_data_row.extend(pdfalto_xml.get_features_for_given_tags(page.tags[tag_index+i],
                                                                                page.tags[tag_index+i+1], page.tags))

                X = np.array([new_data_row]) if X is None else np.concatenate((X, np.array([new_data_row])), axis=0)

                if page.tags[tag_index+context_size].segment_no == page.tags[tag_index+context_size+1].segment_no:
                    y = np.append(y, 1)
                else:
                    y = np.append(y, 0)

        return X, y

    @staticmethod
    def get_feature_matrix(pdf_features_list: List[PdfFeatures], model_configs: Dict):
        X_train = None
        y_train = np.array([])

        for pdf_features in pdf_features_list:
            X_sub, y_sub = LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features.__get_training_data(pdf_features, model_configs)
            if X_sub is None:
                print(f'File has no data')
                continue
            X_train = X_sub if X_train is None else np.concatenate((X_train, X_sub), axis=0)
            y_train = np.append(y_train, y_sub)

        return LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features(X_train, y_train, model_configs)

    def get_predicted_segments(self, pdfalto_xml, page_tags: List[PdfTag]) -> List[PdfSegment]:

        X = np.array([])
        context_size: int = self.model_configs["context_size"]

        for i in range(context_size):
            page_tags.insert(0, PdfTag(page_tags[0].page_number, "pad_tag", "",
                                       PdfFont("pad_font_id", False, False, 0.0), -i - 1, -i - 1, Rectangle(0, 0, 0, 0), "pad_type"))

        for i in range(context_size):
            page_tags.append(PdfTag(page_tags[0].page_number, "pad_tag", "",
                                    PdfFont("pad_font_id", False, False, 0.0), -i - 1000, -i - 1000, Rectangle(0, 0, 0, 0), "pad_type"))

        for tag_index, tag in enumerate(page_tags):
            if tag_index + (2*context_size+2) > len(page_tags):
                continue

            new_data_row = []

            for i in range(2 * context_size + 1):
                new_data_row.extend(pdfalto_xml.get_features_for_given_tags(page_tags[tag_index + i],
                                                                            page_tags[tag_index + i + 1], page_tags))

            if len(new_data_row) == 0:
                print(pdfalto_xml.pdf_features.file_name, " - ", str(page_tags[0].page_number))
            X = np.array([new_data_row]) if len(X) == 0 else np.concatenate((X, np.array([new_data_row])), axis=0)

        y = self.model.predict(X) if len(X.shape) == 2 else self.model.predict([X])
        same_paragraph_prediction = [True if prediction > 0.5 else False for prediction in y]

        segments_by_tags = list()
        segments_by_tags.append([page_tags[context_size]])
        for prediction_index, same_paragraph in enumerate(same_paragraph_prediction):
            if same_paragraph:
                segments_by_tags[-1].append(page_tags[prediction_index + context_size + 1])
                continue

            segments_by_tags.append([page_tags[prediction_index + context_size + 1]])

        pdf_segments_for_page: List[PdfSegment] = [PdfSegment.from_segment(pdf_tags) for pdf_tags in segments_by_tags]

        return pdf_segments_for_page

    def predict(self, pdf_features: PdfFeatures) -> List[PdfSegment]:

        pdfalto_xml = PdfAltoXml(pdf_features)

        segments: List[PdfSegment] = list()
        for page in pdf_features.pages:
            if len(page.tags) == 0 or len(page.tags) == 1:
                continue
            segments_for_a_page: List[PdfSegment] = self.get_predicted_segments(pdfalto_xml, deepcopy(page.tags))
            segments.extend(segments_for_a_page)

        return segments

    def get_segments_for_page(self, pdfalto_xml: PdfAltoXml, page_tags: List[PdfTag]) -> List[PdfSegment]:

        return self.get_predicted_segments(pdfalto_xml, deepcopy(page_tags))
