import pathlib

import numpy as np
from typing import List
from copy import deepcopy

from PdfFeatures.PdfFeatures import PdfFeatures
from PdfFeatures.PdfFont import PdfFont
from PdfFeatures.PdfSegment import PdfSegment
from PdfFeatures.PdfTag import PdfTag
from PdfFeatures.Rectangle import Rectangle
from segmentator.get_features import PdfAltoXml

CONTEXT_SIZE = 8
THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


class LightGBM24Features:

    def __init__(self, X_train, y_train, X_test, y_test, model=None, model_name: str = None):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.model = model
        self.model_name = model_name

    @staticmethod
    def __get_training_data(pdf_features: PdfFeatures):

        X = None
        y = np.array([])
        pdfalto_xml = PdfAltoXml(pdf_features)
        print(pdf_features.file_name)

        for _page in pdf_features.pages:

            page = deepcopy(_page)

            for i in range(CONTEXT_SIZE):
                page.tags.insert(0, PdfTag(page.page_number, "pad_tag", "PADFONT",
                                           PdfFont("PADSTYLE", False, False), -i - 1, -i - 1, Rectangle(0, 0, 0, 0)))

            for i in range(CONTEXT_SIZE):
                page.tags.append(PdfTag(page.page_number, "pad_tag", "PADFONT",
                                        PdfFont("PADSTYLE", False, False), -i - 1000, -i - 1000, Rectangle(0, 0, 0, 0)))

            for tag_index, tag in enumerate(page.tags):

                if tag_index + (2 * CONTEXT_SIZE + 2) > len(page.tags):
                    continue

                new_data_row = []

                for i in range(2 * CONTEXT_SIZE + 1):
                    new_data_row.extend(pdfalto_xml.get_features_for_given_tags(page.tags[tag_index + i],
                                                                                page.tags[tag_index + i + 1],
                                                                                page.tags))

                X = np.array([new_data_row]) if X is None else np.concatenate((X, np.array([new_data_row])), axis=0)

                if page.tags[tag_index + CONTEXT_SIZE].segment_no == page.tags[tag_index + CONTEXT_SIZE + 1].segment_no:
                    y = np.append(y, 1)
                else:
                    y = np.append(y, 0)

        return X, y

    @staticmethod
    def get_feature_matrix(pdf_features_list: List[PdfFeatures]):
        X_train = None
        y_train = np.array([])
        X_test = None
        y_test = np.array([])

        for pdf_features in pdf_features_list:
            X_sub, y_sub = LightGBM24Features.__get_training_data(pdf_features)
            if X_sub is None:
                print(f'File has no data')
                continue
            if pdf_features.file_type == "one_column_train" or pdf_features.file_type == "multi_column_train":
                X_train = X_sub if X_train is None else np.concatenate((X_train, X_sub), axis=0)
                y_train = np.append(y_train, y_sub)
            elif pdf_features.file_type == "one_column_test" or pdf_features.file_type == "multi_column_test":
                X_test = X_sub if X_test is None else np.concatenate((X_test, X_sub), axis=0)
                y_test = np.append(y_test, y_sub)

        return LightGBM24Features(X_train, y_train, X_test, y_test)

    def get_predicted_segments(self, pdfalto_xml, page_tags: List[PdfTag]) -> List[PdfSegment]:

        X = None
        context_size: int
        with open(f"{THIS_SCRIPT_PATH}/model_LightGBM_24Features_2021-09-06_18:50:27.txt", "r") as config_file:
            context_size = int(config_file.readlines()[0])

        for i in range(context_size):
            page_tags.insert(0, PdfTag(page_tags[0].page_number, "pad_tag", "PADFONT",
                                       PdfFont("PADSTYLE", False, False, 0), -i - 1, -i - 1, Rectangle(0, 0, 0, 0)))

        for i in range(context_size):
            page_tags.append(PdfTag(page_tags[0].page_number, "pad_tag", "PADFONT",
                                    PdfFont("PADSTYLE", False, False, 0), -i - 1000, -i - 1000, Rectangle(0, 0, 0, 0)))

        for tag_index, tag in enumerate(page_tags):
            if tag_index + (2 * context_size + 2) > len(page_tags):
                continue

            new_data_row = []

            for i in range(2 * context_size + 1):
                new_data_row.extend(pdfalto_xml.get_features_for_given_tags(page_tags[tag_index + i],
                                                                            page_tags[tag_index + i + 1], page_tags))

            X = np.array([new_data_row]) if X is None else np.concatenate((X, np.array([new_data_row])), axis=0)

        y = self.model.predict(X) if len(X.shape) == 2 else self.model.predict([X])
        same_paragraph_prediction = [True if prediction > 0.5 else False for prediction in y]

        segments_by_tags = list()
        segments_by_tags.append([page_tags[context_size]])
        for prediction_index, same_paragraph in enumerate(same_paragraph_prediction):
            if same_paragraph:
                segments_by_tags[-1].append(page_tags[prediction_index + context_size + 1])
                continue

            segments_by_tags.append([page_tags[prediction_index + context_size + 1]])

        segments: List[PdfSegment] = list()

        for segment in segments_by_tags:
            segment_ids = [tag.id for tag in segment]
            text_content = ' '.join([tag.content for tag in segment if tag.content])
            segments.append(
                PdfSegment(page_tags[0].page_number, segment_ids, Rectangle.from_pdftags(segment), text_content))

        return segments

    def predict(self, pdf_features: PdfFeatures) -> List[PdfSegment]:
        pdfalto_xml = PdfAltoXml(pdf_features)

        segments: List[PdfSegment] = list()
        for page in pdf_features.pages:
            if len(page.tags) == 0 or len(page.tags) == 1:
                continue
            segments_for_a_page: List[PdfSegment] = self.get_predicted_segments(pdfalto_xml, deepcopy(page.tags))
            segments.extend(segments_for_a_page)

        return segments
