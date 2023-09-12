import os

from benchmark import loop_pdf_paragraph_tokens
from config import PDF_LABELED_DATA_ROOT_PATH, TRAINED_MODEL_PATH
from paragraph_extraction_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from paragraph_extraction_trainer.load_labeled_data import load_labeled_data
from paragraph_extraction_trainer.model_configuration import MODEL_CONFIGURATION


def train_model():
    pdf_paragraph_tokens_list = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH)

    pdf_features_list = [pdf_paragraph_tokens.pdf_features for pdf_paragraph_tokens in pdf_paragraph_tokens_list]
    trainer = ParagraphExtractorTrainer(pdfs_features=pdf_features_list, model_configuration=MODEL_CONFIGURATION)

    labels = []
    for pdf_paragraph_tokens, token, next_token in loop_pdf_paragraph_tokens(pdf_paragraph_tokens_list):
        labels.append(pdf_paragraph_tokens.check_same_paragraph(token, next_token))
    os.makedirs(TRAINED_MODEL_PATH.parent, exist_ok=True)
    trainer.train(TRAINED_MODEL_PATH, labels)


if __name__ == "__main__":
    train_model()
