import ast
from typing import Dict

import lightgbm as lgb

from huggingface_hub import hf_hub_download

from ServiceConfig import ServiceConfig
from extract_pdf_paragraphs.segmentator.LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features import (
    LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features,
)


def get_model_configs(config_path: str) -> Dict:
    model_configs: {}
    with open(config_path, "r") as config_file:
        config_contents = config_file.read()
        model_configs = ast.literal_eval(config_contents)
    return model_configs


def predict(pdf_features):
    service_config = ServiceConfig()
    model_config_path = hf_hub_download(
        repo_id="HURIDOCS/pdf_segmetation",
        filename="segmentator_model_config.txt",
        revision="52c44568f40ba3c19bd22e5ebc363425b7130a6b",
        cache_dir=service_config.huggingface_path,
    )

    model_configs: {} = get_model_configs(model_config_path)

    segmentation_model_path = hf_hub_download(
        repo_id="HURIDOCS/pdf_segmetation",
        filename="segmentator_model.txt",
        revision="ab83ee7d75e7e1cfe7f0a740d1bf6a3b74a1fdf3",
        cache_dir=service_config.huggingface_path,
    )

    lightgbm_model = lgb.Booster(model_file=segmentation_model_path)
    lightgbm_segmentator = LightGBM_30Features_TagType_OneHotTwoLetter_LightGBM_30Features(
        [], [], model_configs, lightgbm_model
    )

    return lightgbm_segmentator.predict(pdf_features)
