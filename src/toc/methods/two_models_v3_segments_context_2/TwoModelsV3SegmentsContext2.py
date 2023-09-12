from paragraph_extraction_trainer.download_models import toc_model_path
from src.toc.Method import Method
import lightgbm as lgb

from src.toc.methods.two_models_v3_segments_context_2.LightgbmTwoModelsV3SegmentsContext2 import (
    LightgbmTwoModelsV3SegmentsContext2,
)
from toc.PdfSegmentation import PdfSegmentation
from toc.methods.two_models_v3_segments_context_2.SegmentTwoModelsV3SegmentsContext2 import valid_tag_types


class TwoModelsV3SegmentsContext2(Method):
    def train(self, pdfs_segmentations: list[PdfSegmentation]):
        pass

    def predict(self, pdfs_segmentations: list[PdfSegmentation]) -> list[PdfSegmentation]:
        lightgbm_stack_multilingual = LightgbmTwoModelsV3SegmentsContext2()

        model = lgb.Booster(model_file=toc_model_path)
        segments = LightgbmTwoModelsV3SegmentsContext2.get_segments(pdfs_segmentations)

        if not segments:
            return pdfs_segmentations

        predictions = lightgbm_stack_multilingual.predict(model, segments)
        prediction_index = 0

        for pdf_segmentation in pdfs_segmentations:
            for index, segment in enumerate(pdf_segmentation.pdf_segments):
                if segment.token_type not in valid_tag_types:
                    continue

                pdf_segmentation.title_predictions[index] = round(100 * predictions[prediction_index])
                prediction_index += 1

        return pdfs_segmentations
