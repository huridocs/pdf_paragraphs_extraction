from os import listdir
from os.path import join, isdir
from pdf_features.PdfFeatures import PdfFeatures
from config import PARAGRAPH_EXTRACTION_LABELED_DATA_PATH


def loop_datasets(filter_in: str):
    for dataset_name in listdir(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH):
        if filter_in and filter_in not in dataset_name:
            continue

        dataset_path = join(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH, dataset_name)

        if not isdir(dataset_path):
            continue

        yield dataset_name, dataset_path


def load_labeled_data(filter_in: str = None) -> list[PdfFeatures]:
    if filter_in:
        print(f"Loading only datasets with the key word: {filter_in}")
        print()

    pdfs_features: list[PdfFeatures] = list()

    for dataset_name, dataset_path in loop_datasets(filter_in):
        print(f"loading {dataset_name} from {dataset_path}")

        dataset_pdf_name = [(dataset_name, pdf_name) for pdf_name in listdir(dataset_path)]
        for dataset, pdf_name in dataset_pdf_name:
            pdf_features = PdfFeatures.from_labeled_data(PARAGRAPH_EXTRACTION_LABELED_DATA_PATH, dataset, pdf_name)
            pdfs_features.append(pdf_features)

    return pdfs_features
