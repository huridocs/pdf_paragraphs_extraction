from typing import List

from download_models import toc_model_path
from src.toc.PdfFeatures.TocPdfFeatures import TocPdfFeatures
from src.toc.Method import Method
import lightgbm as lgb

from src.toc.PdfFeatures.TagType import TAG_TYPE_DICT
from src.toc.methods.two_models_v3_segments_context_2.LightgbmTwoModelsV3SegmentsContext2 import (
    LightgbmTwoModelsV3SegmentsContext2,
)


class TwoModelsV3SegmentsContext2(Method):
    def train(self, pdfs_features: List[TocPdfFeatures]):
        lightgbm_stack_multilingual = LightgbmTwoModelsV3SegmentsContext2()

        segments = LightgbmTwoModelsV3SegmentsContext2.get_segments(pdfs_features)

        model = lightgbm_stack_multilingual.create_model(segments)
        model.save_model(self.model_path + ".model", num_iteration=model.best_iteration)

    def predict(self, pdfs_features: List[TocPdfFeatures]) -> List[TocPdfFeatures]:
        lightgbm_stack_multilingual = LightgbmTwoModelsV3SegmentsContext2()

        model = lgb.Booster(model_file=toc_model_path)
        segments = LightgbmTwoModelsV3SegmentsContext2.get_segments(pdfs_features)

        if not segments:
            return pdfs_features

        labels = lightgbm_stack_multilingual.predict(model, segments)

        valid_tag_types = [TAG_TYPE_DICT["title"], TAG_TYPE_DICT["text"], TAG_TYPE_DICT["list"]]

        all_segments = [
            segment
            for pdf_feature in pdfs_features
            for segment in pdf_feature.pdf_segments
            if segment.segment_type in valid_tag_types
        ]

        for probability, segment in zip(labels, all_segments):
            segment.ml_label = 0 if probability < 0.5 else 1
            segment.ml_percentage = round(100 * probability)

        return pdfs_features
