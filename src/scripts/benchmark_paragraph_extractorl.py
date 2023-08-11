import os
from os.path import join, exists
from pathlib import Path
from time import time

from pdf_features.PdfFeatures import PdfFeatures
from pdf_token_type_labels.load_labeled_data import load_labeled_data
from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration

from sklearn.metrics import f1_score, accuracy_score

from config import PDF_LABELED_DATA_ROOT_PATH, ROOT_PATH
from extract_pdf_paragraphs.ParagraphExtractorTrainer import ParagraphExtractorTrainer

BENCHMARK_MODEL_PATH = Path(join(ROOT_PATH, "model", "paragraph_extraction_benchmark.model"))
MODEL_CONFIGURATION = ModelConfiguration()


def train_for_benchmark():
    pdfs_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH, filter_in="train")
    model_configuration = MODEL_CONFIGURATION
    trainer = ParagraphExtractorTrainer(pdfs_features=pdfs_features, model_configuration=model_configuration)
    os.makedirs(BENCHMARK_MODEL_PATH.parent, exist_ok=True)
    trainer.train(str(BENCHMARK_MODEL_PATH))


def loop_tokens(test_pdf_features: list[PdfFeatures]):
    for pdf_features in test_pdf_features:
        for page in pdf_features.pages:
            if len(page.tokens) < 2:
                continue

            for token, next_token in zip(page.tokens, page.tokens[1:]):
                yield token, next_token


def predict_for_benchmark():
    test_pdf_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    truths = [token.segment_no == token.segment_no for token, next_token in loop_tokens(test_pdf_features)]

    print("predicting")
    trainer = ParagraphExtractorTrainer(test_pdf_features, MODEL_CONFIGURATION)
    trainer.predict(str(BENCHMARK_MODEL_PATH))

    predictions = [token.prediction for token, next_token in loop_tokens(test_pdf_features)]
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
    print("finished in", time() - start, "seconds")
