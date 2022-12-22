import ast
from typing import Dict, List

import lightgbm as lgb
from download_models import segmentation_model_config_path, segmentation_model_path
from extract_pdf_paragraphs.PdfFeatures.PdfSegment import PdfSegment
from extract_pdf_paragraphs.segmentator.LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features import (
    LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features,
)


def get_model_configs(config_path: str) -> Dict:
    model_configs: {}
    with open(config_path, "r") as config_file:
        config_contents = config_file.read()
        model_configs = ast.literal_eval(config_contents)
    return model_configs


def predict(pdf_features) -> List[PdfSegment]:
    model_configs: {} = get_model_configs(segmentation_model_config_path)

    lightgbm_model = lgb.Booster(model_file=segmentation_model_path)
    lightgbm_segmentator = LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features(
        [], [], model_configs, lightgbm_model
    )

    return lightgbm_segmentator.predict(pdf_features)
