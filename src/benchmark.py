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

BENCHMARK_MODEL_PATH = Path(join(ROOT_PATH, "model", "paragraph_extraction_benchmark.model"))


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

    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)

    labels = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        labels.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))
    os.makedirs(BENCHMARK_MODEL_PATH.parent, exist_ok=True)
    trainer.train(str(BENCHMARK_MODEL_PATH), labels)


def predict_for_benchmark(pdf_paragraph_tokens_list: list[PdfParagraphTokens], get_granular_scores: bool):
    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)
    truths = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        truths.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))

    print("predicting")
    start_time = time()
    trainer.predict(BENCHMARK_MODEL_PATH)
    predictions = [token.prediction for token in trainer.loop_tokens()]
    total_time = time() - start_time
    if get_granular_scores:
        benchmark_table = BenchmarkTable(pdf_paragraph_tokens_list, total_time)
        benchmark_table.prepare_benchmark_table()

    return truths, predictions


def benchmark(get_granular_scores: bool):
    train_for_benchmark()
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    truths, predictions = predict_for_benchmark(pdf_paragraph_tokens_list, get_granular_scores)

    f1 = round(f1_score(truths, predictions, average="macro") * 100, 2)
    accuracy = round(accuracy_score(truths, predictions) * 100, 2)
    print(f"F1 score {f1}%")
    print(f"Accuracy score {accuracy}%")


if __name__ == "__main__":
    print("start")
    start = time()
    benchmark(get_granular_scores=True)
    print("finished in", int(time() - start), "seconds")
