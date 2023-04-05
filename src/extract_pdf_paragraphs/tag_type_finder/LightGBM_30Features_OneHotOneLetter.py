import numpy as np
from typing import List, Dict


from copy import deepcopy

from extract_pdf_paragraphs.PdfFeatures.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.PdfFeatures.PdfFont import PdfFont
from extract_pdf_paragraphs.PdfFeatures.PdfTag import PdfTag
from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle
from extract_pdf_paragraphs.tag_type_finder.get_features import PdfAltoXml

tag_type_dict: Dict = {
    "text": 6,
    "title": 5,
    "figure": 4,
    "table": 3,
    "list": 2,
    "footnote": 1,
    "formula": 0,
    "code": 3,
}

tag_type_by_index: Dict = {6: "text", 5: "title", 4: "figure", 3: "table", 2: "list", 1: "footnote", 0: "formula"}


class LightGBM_30Features_OneHotOneLetter:
    def __init__(self, X_train, y_train, model_configs: Dict, model=None, benchmarking=False):
        self.X_train = X_train
        self.y_train = y_train
        self.model_configs = model_configs
        self.model = model
        self.benchmarking = benchmarking
        self.tag_type_counts = {}
        self.wrong_prediction_counts = {}

    def get_predicted_tag_types(
        self, pdfalto_xml, page_tags: List[PdfTag], predicted_tag_types: Dict = dict
    ) -> Dict[str, str]:
        # X = None
        context_size: int = self.model_configs["context_size"]
        data_rows = []

        for i in range(context_size):
            page_tags.insert(
                0,
                PdfTag(
                    page_tags[0].page_number,
                    "pad_tag",
                    "",
                    PdfFont("pad_font_id", False, False, 0.0),
                    -i - 1,
                    -i - 1,
                    Rectangle(0, 0, 0, 0),
                    "pad_type",
                ),
            )

        for i in range(context_size + 1):
            page_tags.append(
                PdfTag(
                    page_tags[0].page_number,
                    "pad_tag",
                    "",
                    PdfFont("pad_font_id", False, False, 0.0),
                    -i - 1000,
                    -i - 1000,
                    Rectangle(0, 0, 0, 0),
                    "pad_type",
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

            data_rows.append(new_data_row)

            # X = np.array([new_data_row]) if X is None else np.concatenate((X, np.array([new_data_row])), axis=0)

        X = np.zeros(((len(data_rows)), len(data_rows[0])))
        for i, v in enumerate(data_rows):
            X[i] = v

        y = self.model.predict(X) if len(X.shape) == 2 else self.model.predict([X])
        for tag_index, tag in enumerate(page_tags):
            if tag.id == "pad_tag":
                continue
            predicted_tag_types[tag.id] = tag_type_by_index[np.argmax(y[tag_index - context_size])]

        if self.benchmarking:
            if pdfalto_xml.pdf_features.file_type not in self.tag_type_counts.keys():
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type] = {}
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["text"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["title"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["figure"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["table"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["list"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["footnote"] = 0
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type]["formula"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type] = {}
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["text"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["title"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["figure"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["table"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["list"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["footnote"] = 0
                self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type]["formula"] = 0

            for tag_index, tag in enumerate(page_tags):
                if tag.id == "pad_tag":
                    continue
                if tag.tag_type == "not_found":
                    continue
                self.tag_type_counts[pdfalto_xml.pdf_features.file_type][tag.tag_type] += 1
                if tag.tag_type != predicted_tag_types[tag.id]:
                    self.wrong_prediction_counts[pdfalto_xml.pdf_features.file_type][tag.tag_type] += 1

        return predicted_tag_types

    def predict(self, pdf_features: PdfFeatures) -> Dict[str, str]:
        pdfalto_xml = PdfAltoXml(pdf_features)
        predicted_tag_types: Dict[str, str] = dict()
        for page in pdf_features.pages:
            if len(page.tags) == 0:
                continue
            predicted_tag_types = self.get_predicted_tag_types(pdfalto_xml, deepcopy(page.tags), predicted_tag_types)
            # predicted_tag_types = self.get_predicted_tag_types(pdfalto_xml, page.tags, predicted_tag_types) # 4% faster execution time

        return predicted_tag_types
