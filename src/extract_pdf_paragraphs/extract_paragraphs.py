import os
import pathlib
import shutil

from pdf_features.PdfFeatures import PdfFeatures
from pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer

import config
from data.ExtractionData import ExtractionData
from data.Task import Task
from extract_pdf_paragraphs.segmentator.predict import predict

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def get_paths(tenant: str, pdf_file_name: str):
    file_name = pdf_file_name.replace(".", "")
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


def extract_paragraphs(task: Task):
    pdf_file_path, xml_file_path, failed_pdf_path = get_paths(task.tenant, task.params.filename)

    os.makedirs("/".join(xml_file_path.split("/")[:-1]), exist_ok=True)
    pdf_features = PdfFeatures.from_pdf_path(pdf_file_path, xml_file_path)

    if conversion_failed(xml_file_path, pdf_file_path, failed_pdf_path):
        return None

    TokenTypeTrainer(pdf_features).predict()
    pdf_segments = predict(pdf_features)

    segments = [x.to_segment_box() for x in pdf_segments]

    extraction_data = ExtractionData(
        tenant=task.tenant,
        file_name=task.params.filename,
        paragraphs=segments,
        page_width=pdf_features.pages[0].page_width if pdf_features.pages else 0,
        page_height=pdf_features.pages[0].page_height if pdf_features.pages else 0,
    )

    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)

    return extraction_data
