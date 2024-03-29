import numpy as np

import lightgbm as lgb

from src.toc.methods.two_models_v3_segments_context_2.SegmentTwoModelsV3SegmentsContext2 import (
    SegmentTwoModelsV3SegmentsContext2,
)
from toc.PdfSegmentation import PdfSegmentation


class LightgbmTwoModelsV3SegmentsContext2:
    def __init__(self):
        self.segments_two_models: list[SegmentTwoModelsV3SegmentsContext2] = list()
        self.model = None
        self.best_cut = 0

    def create_model(self, training_segments: list[SegmentTwoModelsV3SegmentsContext2]):
        self.segments_two_models = training_segments

        if len(self.segments_two_models) == 0:
            return None

        self.run_light_gbm()

        return self.model

    @staticmethod
    def set_model(x_train, y_train):
        y_train = y_train.astype(int)

        parameters = dict()
        parameters["num_leaves"] = 70
        parameters["feature_fraction"] = 0.9
        parameters["bagging_fraction"] = 0.9
        parameters["bagging_freq"] = 0
        parameters["objective"] = "binary"
        parameters["learning_rate"] = 0.05
        parameters["metric"] = "binary_logloss"
        parameters["verbose"] = -1
        parameters["boosting_type"] = "gbdt"

        # clf = lgb.LGBMClassifier(num_leaves=70, learning_rate=0.05, random_state=42, n_estimators=300)
        train_data = lgb.Dataset(x_train, y_train)
        num_round = 300
        light_gbm_model = lgb.train(parameters, train_data, num_round)
        # light_gbm_model = clf.fit(x_train, y_train)

        return light_gbm_model

    def run_light_gbm(self):
        x_train, y_train = self.get_training_data()
        self.model = self.set_model(x_train, y_train)

    def get_training_data(self):
        y = np.array([])
        x_rows = []
        for segment in self.segments_two_models:
            x_rows.append(segment.get_features_array())
            y = np.append(y, 0)

        X = np.zeros((len(x_rows), len(x_rows[0]) if x_rows else 0))
        for i, v in enumerate(x_rows):
            X[i] = v

        return X, y

    @staticmethod
    def get_segments(pdfs_segmentations: list[PdfSegmentation]):
        segments = list()
        for pdf_segmentation in pdfs_segmentations:
            segments.extend(SegmentTwoModelsV3SegmentsContext2.from_pdf_segments(pdf_segmentation))

        return segments

    def predict(self, model, testing_segments: list[SegmentTwoModelsV3SegmentsContext2]):
        self.segments_two_models = testing_segments
        x, y = self.get_training_data()
        x = x[:, : model.num_feature()]
        predictions = model.predict(x)
        return predictions
