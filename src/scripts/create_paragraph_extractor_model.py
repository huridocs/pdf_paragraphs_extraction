import os

from pdf_token_type_labels.load_labeled_data import load_labeled_data

from config import TRAINED_MODEL_PATH, PDF_LABELED_DATA_ROOT_PATH
from extract_pdf_paragraphs.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from extract_pdf_paragraphs.model_configuration import MODEL_CONFIGURATION


def train_model():
    pdfs_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH)
    trainer = ParagraphExtractorTrainer(pdfs_features=pdfs_features, model_configuration=MODEL_CONFIGURATION)
    os.makedirs(TRAINED_MODEL_PATH.parent, exist_ok=True)
    trainer.train(TRAINED_MODEL_PATH)


if __name__ == "__main__":
    train_model()
