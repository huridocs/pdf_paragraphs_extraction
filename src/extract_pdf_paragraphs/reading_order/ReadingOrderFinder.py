import numpy as np
from typing import List, Dict
from copy import deepcopy

from download_models import reading_order_model_path, next_tag_model_path
from extract_pdf_paragraphs.pdf_features.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.pdf_features.PdfFont import PdfFont
from extract_pdf_paragraphs.pdf_features.PdfTag import PdfTag
from extract_pdf_paragraphs.pdf_features.Rectangle import Rectangle
from extract_pdf_paragraphs.reading_order.get_features_reading_order import PdfAltoXml
from extract_pdf_paragraphs.reading_order.get_features_possible_next_tag_selector import get_next_tag_features
import lightgbm as lgb


class ReadingOrderFinder:
    def __init__(self):
        self.model = lgb.Booster(model_file=reading_order_model_path)
        self.possible_next_tag_model = lgb.Booster(model_file=next_tag_model_path)
        self.features_cache: dict[tuple, float] = dict()
        self.page_tags = list()
        self.pdfalto_xml = None
        self.tags_by_id = dict()

    def __get_next_possible_18_tag_ids(self, not_assigned_tags_ids: list[str], previous_tag: PdfTag) -> List[str]:
        X = np.array([])
        predictions_ids: list[tuple] = list()
        predictions_already_cached = list()
        for tag_id in not_assigned_tags_ids:
            key = (previous_tag.id, tag_id)

            if key in self.features_cache:
                predictions_already_cached.append(self.features_cache[key])
                continue

            new_data_row = get_next_tag_features(previous_tag, self.tags_by_id[tag_id])
            X = np.array([new_data_row]) if len(X) == 0 else np.concatenate((X, np.array([new_data_row])), axis=0)
            predictions_ids.append(key)

        if len(X) > 0:
            y = self.possible_next_tag_model.predict(X) if len(X.shape) == 2 else self.possible_next_tag_model.predict([X])

            for prediction_ids, y1 in zip(predictions_ids, y):
                self.features_cache[prediction_ids] = y1
        else:
            y = []

        next_possible_18_tag_ids: List[str] = list()
        best_18_indexes = np.argsort([list(y) + predictions_already_cached], axis=1)[:, -18:]
        for prediction_index in best_18_indexes[0]:
            next_possible_18_tag_ids.append(not_assigned_tags_ids[prediction_index])

        return next_possible_18_tag_ids

    def __get_reading_order_for_page(self) -> List[PdfTag]:
        self.tags_by_id: Dict[str, PdfTag] = {tag.id: tag for tag in self.page_tags}
        current_tag: PdfTag = self.get_pad_tag()
        self.tags_by_id["pad_tag"] = deepcopy(current_tag)
        not_assigned_tags_ids: List[str] = [tag.id for tag in self.page_tags] + [self.get_pad_tag().id] * 17
        predicted_reading_order_for_page: List[PdfTag] = []

        while len(not_assigned_tags_ids) >= 18:
            next_tags_candidates_ids: List[str] = self.__get_next_possible_18_tag_ids(not_assigned_tags_ids, current_tag)
            next_tags_candidates_ids = [tag_id for tag_id in next_tags_candidates_ids if tag_id != "pad_tag"]
            next_tag: PdfTag = self.tags_by_id[next_tags_candidates_ids[0]]

            for possible_next_tag_id in next_tags_candidates_ids[1:]:
                possible_next_tag: PdfTag = self.tags_by_id[possible_next_tag_id]

                y = self.get_prediction_reading_order(current_tag, next_tag, self.tags_by_id[possible_next_tag_id])

                if y > 0.5:
                    next_tag = possible_next_tag

            current_tag = next_tag

            predicted_reading_order_for_page.append(current_tag)
            not_assigned_tags_ids.remove(current_tag.id)

        return predicted_reading_order_for_page

    def get_prediction_reading_order(self, current_tag, next_tag, possible_next_tag):
        new_data_row = self.pdfalto_xml.get_features_for_given_tags(self.page_tags, current_tag, next_tag, possible_next_tag)
        y = self.model.predict(np.array([new_data_row]))
        return y[0]

    def get_reading_order_from_pdf_features(self, pdf_features: PdfFeatures):
        self.pdfalto_xml = PdfAltoXml(pdf_features)

        for page in pdf_features.pages:
            if len(page.tags) == 0:
                continue
            self.page_tags = page.tags

            predicted_reading_order_for_page: List[PdfTag] = self.__get_reading_order_for_page()
            page.tags = predicted_reading_order_for_page

        return pdf_features

    def get_pad_tag(self):
        return PdfTag(
            self.page_tags[0].page_number,
            "pad_tag",
            "",
            PdfFont("pad_font_id", False, False, 0.0),
            -1000,
            -1000,
            Rectangle(9999, 9999, 9999, 9999),
            "pad_type",
            list(),
        )
