import random
from os.path import join
from pathlib import Path
from time import time

import numpy as np

from download_models import next_tag_model_path
from extract_pdf_paragraphs.pdf_features.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.reading_order.ReadingOrderFinder import ReadingOrderFinder
import lightgbm as lgb


def benchmark_reading_order():
    pdf_features = PdfFeatures.from_pdfalto(join(Path(__file__).parent, "two_column.xml"))

    start = time()
    print("start")
    for i in range(1):
        ReadingOrderFinder().get_reading_order_from_pdf_features(pdf_features)

    print("finished in", time() - start, "seconds")


def benchmark_predict():
    model = lgb.Booster(model_file=next_tag_model_path)

    start = time()

    X = np.array([])
    for i in range(300):
        new_data_row = [random.random() * 100 for _ in range(9)]
        X = np.array([new_data_row]) if len(X) == 0 else np.concatenate((X, np.array([new_data_row])), axis=0)

    for j in range(1000):
        for _ in range(1):
            model.predict(X)

    print(f"predict {round(time() - start, 3)} seconds")


if __name__ == "__main__":
    # print(Path(__file__).parent)
    benchmark_reading_order()
