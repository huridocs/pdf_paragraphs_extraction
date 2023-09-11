import os
import pathlib
import shutil

from pdf_features.PdfFeatures import PdfFeatures

import config
from data.ExtractionData import ExtractionData
from data.SegmentBox import SegmentBox
from data.Task import Task

from download_models import paragraph_extraction_model_path
from paragraph_extraction_trainer.ParagraphExtractorTrainer import ParagraphExtractorTrainer
from paragraph_extraction_trainer.model_configuration import MODEL_CONFIGURATION
from toc.PdfSegmentation import PdfSegmentation

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def get_paths(tenant: str, pdf_file_name: str):
    file_name = pdf_file_name.replace(".pdf", "").replace(".", "")
    pdf_file_path = f"{config.DATA_PATH}/to_extract/{tenant}/{pdf_file_name}"
    xml_file_path = f"{config.DATA_PATH}/xml/{tenant}/{file_name}.xml"
    failed_pdf_path = f"{config.DATA_PATH}/failed_pdf/{tenant}/{pdf_file_name}"
    return pdf_file_path, xml_file_path, failed_pdf_path


def conversion_failed(xml_file_path, pdf_file_path, failed_pdf_path):
    if os.path.exists(xml_file_path):
        return False

    if os.path.exists(pdf_file_path):
        os.makedirs("/".join(failed_pdf_path.split("/")[:-1]), exist_ok=True)
        shutil.move(pdf_file_path, failed_pdf_path)

    return True


def extract_paragraphs(pdf_path):
    pdf_features = PdfFeatures.from_pdf_path(pdf_path)
    trainer = ParagraphExtractorTrainer(pdfs_features=[pdf_features], model_configuration=MODEL_CONFIGURATION)
    trainer.predict(paragraph_extraction_model_path)
    pdf_segments = trainer.get_pdf_segments(paragraph_extraction_model_path)
    pdf_segmentation = PdfSegmentation(pdf_features=pdf_features, pdf_segments=pdf_segments)
    return pdf_segmentation


def extract_paragraphs_asynchronous(task: Task):
    pdf_file_path, xml_file_path, failed_pdf_path = get_paths(task.tenant, task.params.filename)

    os.makedirs("/".join(xml_file_path.split("/")[:-1]), exist_ok=True)
    pdf_features = PdfFeatures.from_pdf_path(pdf_file_path, xml_file_path)

    if conversion_failed(xml_file_path, pdf_file_path, failed_pdf_path):
        return None

    trainer = ParagraphExtractorTrainer([pdf_features], MODEL_CONFIGURATION)
    pdf_segments = trainer.get_pdf_segments(paragraph_extraction_model_path)

    extraction_data = ExtractionData(
        tenant=task.tenant,
        file_name=task.params.filename,
        paragraphs=[SegmentBox.from_pdf_segment(pdf_segment) for pdf_segment in pdf_segments],
        page_width=pdf_features.pages[0].page_width if pdf_features.pages else 0,
        page_height=pdf_features.pages[0].page_height if pdf_features.pages else 0,
    )

    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)

    return extraction_data
