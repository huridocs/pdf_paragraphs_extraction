import os
from os.path import join, isdir
from os import listdir
from pathlib import Path
from time import time
from extract_pdf_paragraphs.PdfParagraphTokens import PdfParagraphTokens

from sklearn.metrics import f1_score, accuracy_score

from config import PDF_LABELED_DATA_ROOT_PATH, ROOT_PATH, PARAGRAPH_EXTRACTION_LABELED_DATA_PATH
from extract_pdf_paragraphs.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from extract_pdf_paragraphs.model_configuration import MODEL_CONFIGURATION

BENCHMARK_MODEL_PATH = Path(join(ROOT_PATH, "model", "paragraph_extraction_benchmark.model"))


def loop_datasets(filter_in: str):
    for dataset_name in listdir(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH):
        if filter_in and filter_in not in dataset_name:
            continue

        dataset_path = join(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH, dataset_name)

        if not isdir(dataset_path):
            continue

        yield dataset_name, dataset_path


def load_labeled_data(filter_in: str = None) -> list[PdfParagraphTokens]:
    if filter_in:
        print(f"Loading only datasets with the key word: {filter_in}")
        print()

    pdf_paragraph_tokens_list: list[PdfParagraphTokens] = list()

    for dataset_name, dataset_path in loop_datasets(filter_in):
        print(f"loading {dataset_name} from {dataset_path}")

        dataset_pdf_name = [(dataset_name, pdf_name) for pdf_name in listdir(dataset_path)]
        for dataset, pdf_name in dataset_pdf_name:
            pdf_paragraph_tokens = PdfParagraphTokens.from_labeled_data(dataset, pdf_name)
            pdf_paragraph_tokens_list.append(pdf_paragraph_tokens)

    return pdf_paragraph_tokens_list


def loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list: list[PdfParagraphTokens]):
    for pdf_paragraph_tokens in pdf_paragraph_tokens_list:
        for page in pdf_paragraph_tokens.pdf_features.pages:
            if not page.tokens:
                continue
            for token, next_token in zip(page.tokens, page.tokens[1:]):
                yield pdf_paragraph_tokens, token, next_token
            yield pdf_paragraph_tokens, page.tokens[-1], page.tokens[-1]


def train_for_benchmark():
    pdf_paragraph_tokens_list = load_labeled_data(filter_in="train")

    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)

    labels = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        labels.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))
    os.makedirs(BENCHMARK_MODEL_PATH.parent, exist_ok=True)
    trainer.train(str(BENCHMARK_MODEL_PATH), labels)


def predict_for_benchmark():
    pdf_paragraph_tokens_list = load_labeled_data(filter_in="test")
    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)
    truths = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        truths.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))

    print("predicting")
    trainer.predict(BENCHMARK_MODEL_PATH)
    predictions = [token.prediction for token in trainer.loop_tokens()]
    print(len(truths))
    print(len(predictions))
    return truths, predictions


def benchmark():
    # train_for_benchmark()
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
