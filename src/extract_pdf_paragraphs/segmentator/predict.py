import pathlib

import lightgbm as lgb

from extract_pdf_paragraphs.segmentator.LightGBM24Features import LightGBM24Features

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def predict(pdf_features):
    lightgbm_model = lgb.Booster(
        model_file=f"{THIS_SCRIPT_PATH}/model/model_LightGBM_24Features_2021-09-06_18:50:27.txt"
    )
    lgb_24_features = LightGBM24Features([], [], [], [], model=lightgbm_model)
    return lgb_24_features.predict(pdf_features)
