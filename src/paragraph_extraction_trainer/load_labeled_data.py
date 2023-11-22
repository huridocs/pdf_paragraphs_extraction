from paragraph_extraction_trainer.PdfParagraphTokens import PdfParagraphTokens
from os import listdir
from os.path import join, isdir
from paragraph_extraction_trainer.trainer_paths import PARAGRAPH_EXTRACTION_RELATIVE_PATH


def loop_datasets(paragraph_extraction_labeled_data_path: str, filter_in: str):
    print(paragraph_extraction_labeled_data_path)
    for dataset_name in listdir(paragraph_extraction_labeled_data_path):
        if filter_in and filter_in not in dataset_name:
            continue

        dataset_path = join(paragraph_extraction_labeled_data_path, dataset_name)

        if not isdir(dataset_path):
            continue

        yield dataset_name, dataset_path


def load_labeled_data(pdf_labeled_data_root_path: str, filter_in: str = None) -> list[PdfParagraphTokens]:
    if filter_in:
        print(f"Loading only datasets with the key word: {filter_in}")
        print()

    pdf_paragraph_tokens_list: list[PdfParagraphTokens] = list()
    paragraph_extraction_labeled_data_path: str = join(pdf_labeled_data_root_path, PARAGRAPH_EXTRACTION_RELATIVE_PATH)

    for dataset_name, dataset_path in loop_datasets(paragraph_extraction_labeled_data_path, filter_in):
        print(f"loading {dataset_name} from {dataset_path}")

        dataset_pdf_name = [(dataset_name, pdf_name) for pdf_name in listdir(dataset_path)]
        for dataset, pdf_name in dataset_pdf_name:
            pdf_paragraph_tokens = PdfParagraphTokens.from_labeled_data(pdf_labeled_data_root_path, dataset, pdf_name)
            pdf_paragraph_tokens_list.append(pdf_paragraph_tokens)

    return pdf_paragraph_tokens_list
