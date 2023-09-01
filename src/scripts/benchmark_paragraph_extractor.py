import os
from os.path import join
from pathlib import Path
from time import time

from pdf_token_type_labels.load_labeled_data import load_labeled_data

from sklearn.metrics import f1_score, accuracy_score

from config import PDF_LABELED_DATA_ROOT_PATH, ROOT_PATH
from extract_pdf_paragraphs.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from extract_pdf_paragraphs.model_configuration import MODEL_CONFIGURATION

BENCHMARK_MODEL_PATH = Path(join(ROOT_PATH, "model", "paragraph_extraction_benchmark.model"))


def train_for_benchmark():
    pdfs_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH, filter_in="train")
    trainer = ParagraphExtractorTrainer(pdfs_features=pdfs_features, model_configuration=MODEL_CONFIGURATION)
    os.makedirs(BENCHMARK_MODEL_PATH.parent, exist_ok=True)
    trainer.train(str(BENCHMARK_MODEL_PATH))


def predict_for_benchmark():
    test_pdf_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    trainer = ParagraphExtractorTrainer(pdfs_features=test_pdf_features, model_configuration=MODEL_CONFIGURATION)
    truths = [token.segment_no == next_token.segment_no for token, next_token in trainer.loop_token_next_token()]

    print("predicting")
    trainer.predict(BENCHMARK_MODEL_PATH)

    predictions = [token.prediction for token, next_token in trainer.loop_token_next_token()]
    return truths, predictions


def benchmark():
    train_for_benchmark()
    truths, predictions = predict_for_benchmark()

    f1 = round(f1_score(truths, predictions, average="macro") * 100, 2)
    accuracy = round(accuracy_score(truths, predictions) * 100, 2)
    print(f"F1 score {f1}%")
    print(f"Accuracy score {accuracy}%")


if __name__ == "__main__":
    start = time()
    print("start")
    benchmark()
    print("finished in", int(time() - start), "seconds")
