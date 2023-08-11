import os
from os.path import join, exists

from pdf_token_type_labels.load_labeled_data import load_labeled_data
from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration

from config import PDF_LABELED_DATA_ROOT_PATH, TRAINED_MODEL_PATH
from extract_pdf_paragraphs.ParagraphExtractorTrainer import ParagraphExtractorTrainer


def train_model():
    pdfs_features = load_labeled_data(pdf_labeled_data_project_path=PDF_LABELED_DATA_ROOT_PATH, filter_in="train")
    model_configuration = ModelConfiguration()
    trainer = ParagraphExtractorTrainer(pdfs_features=pdfs_features, model_configuration=model_configuration)
    os.makedirs(TRAINED_MODEL_PATH.parent, exist_ok=True)
    trainer.train(TRAINED_MODEL_PATH)


if __name__ == '__main__':
    train_model()
