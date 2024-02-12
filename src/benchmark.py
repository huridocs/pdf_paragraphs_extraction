import os
from os.path import join
from pathlib import Path
from time import time
from BenchmarkTable import BenchmarkTable
from paragraph_extraction_trainer.PdfParagraphTokens import PdfParagraphTokens
from sklearn.metrics import f1_score, accuracy_score
from config import ROOT_PATH, PDF_LABELED_DATA_ROOT_PATH
from paragraph_extraction_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from paragraph_extraction_trainer.load_labeled_data import load_labeled_data
from paragraph_extraction_trainer.model_configuration import MODEL_CONFIGURATION

BENCHMARK_MODEL_PATH = Path(join(ROOT_PATH, "model", "benchmark.model"))


def loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list: list[PdfParagraphTokens]):
    for pdf_paragraph_tokens in pdf_paragraph_tokens_list:
        for page in pdf_paragraph_tokens.pdf_features.pages:
            if not page.tokens:
                continue
            for token, next_token in zip(page.tokens, page.tokens[1:]):
                yield pdf_paragraph_tokens, token, next_token
            yield pdf_paragraph_tokens, page.tokens[-1], page.tokens[-1]


def train_for_benchmark():
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="train")
    print("length of pdf paragraphs for training", len(pdf_paragraph_tokens_list))
    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)

    labels = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        labels.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))
    os.makedirs(BENCHMARK_MODEL_PATH.parent, exist_ok=True)
    trainer.train(str(BENCHMARK_MODEL_PATH), labels)


def train():
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH)
    print("length of pdf paragraphs for training", len(pdf_paragraph_tokens_list))
    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)

    labels = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        labels.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))
    model_path = Path(join(ROOT_PATH, "model", "all_data.model"))
    trainer.train(str(model_path), labels)


def predict_for_benchmark(pdf_paragraph_tokens_list: list[PdfParagraphTokens], model_path: str = ""):
    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)
    truths = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        truths.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))

    print("predicting")
    start_time = time()
    if model_path:
        trainer.predict(model_path)
    else:
        trainer.predict(BENCHMARK_MODEL_PATH)
    predictions = [token.prediction for token in trainer.loop_tokens()]
    total_time = time() - start_time
    benchmark_table = BenchmarkTable(pdf_paragraph_tokens_list, total_time)
    benchmark_table.prepare_benchmark_table()

    return truths, predictions


def benchmark():
    train_for_benchmark()
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    truths, predictions = predict_for_benchmark(pdf_paragraph_tokens_list)

    f1 = round(f1_score(truths, predictions, average="macro") * 100, 2)
    accuracy = round(accuracy_score(truths, predictions) * 100, 2)
    print(f"F1 score {f1}%")
    print(f"Accuracy score {accuracy}%")


def benchmark_all():
    train_for_benchmark()
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    model_path = str(Path(join(ROOT_PATH, "model", "all_data.model")))
    truths, predictions = predict_for_benchmark(pdf_paragraph_tokens_list, model_path)

    f1 = round(f1_score(truths, predictions, average="macro") * 100, 2)
    accuracy = round(accuracy_score(truths, predictions) * 100, 2)
    print(f"F1 score {f1}%")
    print(f"Accuracy score {accuracy}%")


if __name__ == "__main__":
    print("start")
    start = time()
    benchmark_all()
    print("finished in", int(time() - start), "seconds")
