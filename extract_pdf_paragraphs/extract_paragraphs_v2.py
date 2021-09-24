import os
import pathlib
import platform
import shutil
import subprocess

from PdfFeatures.PdfFeatures import PdfFeatures
from data.ExtractionData import ExtractionData
from data.SegmentBox import SegmentBox
from data.Task import Task
from segmentator.LightGBM24Features import LightGBM24Features
from segmentator.predict import predict

ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKER_VOLUME = f'{ROOT_DIRECTORY}/docker_volume'
THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def get_paths(tenant: str, pdf_file_name: str):
    file_name = ''.join(pdf_file_name.split('.')[:-1])
    pdf_file_path = f'{DOCKER_VOLUME}/to_extract/{tenant}/{pdf_file_name}'
    xml_file_path = f'{DOCKER_VOLUME}/xml/{tenant}/{file_name}.xml'
    failed_pdf_path = f'{DOCKER_VOLUME}/failed_pdf/{tenant}/{pdf_file_name}'
    return pdf_file_path, xml_file_path, failed_pdf_path


def conversion_failed(xml_file_path, pdf_file_path, failed_pdf_path):
    if os.path.exists(xml_file_path):
        return False

    if os.path.exists(pdf_file_path):
        os.makedirs('/'.join(failed_pdf_path.split('/')[:-1]), exist_ok=True)
        shutil.move(pdf_file_path, failed_pdf_path)

    return True


def convert_to_xml(pdf_file_path: str, xml_file_path: str, failed_pdf_path: str):
    os.makedirs('/'.join(xml_file_path.split('/')[:-1]), exist_ok=True)

    if platform.system() == 'Darwin':
        pdfalto_executable = f'{THIS_SCRIPT_PATH}/pdfalto/pdfalto_macos'
    else:
        pdfalto_executable = f'{THIS_SCRIPT_PATH}/pdfalto/pdfalto_linux'

    subprocess.run([pdfalto_executable, '-readingOrder', pdf_file_path, xml_file_path])

    if conversion_failed(xml_file_path, pdf_file_path, failed_pdf_path):
        return False

    remove_xml_metadata(xml_file_path)
    return True


def remove_xml_metadata(xml_file_path):
    file_xml_metadata_path = xml_file_path.replace('.xml', '_metadata.xml')
    file_xml_data_path = xml_file_path.replace('.xml', '.xml_data')
    if os.path.exists(file_xml_metadata_path):
        os.remove(file_xml_metadata_path)
    shutil.rmtree(file_xml_data_path, ignore_errors=True)


def extract_paragraphs_v2(task: Task):
    pdf_file_path, xml_file_path, failed_pdf_path = get_paths(task.tenant, task.pdf_file_name)

    if not convert_to_xml(pdf_file_path, xml_file_path, failed_pdf_path):
        return None

    pdf_features = PdfFeatures.from_pdfalto(xml_file_path)
    pdf_segments = predict(pdf_features)
    segments = [SegmentBox.from_pdf_segment(x) for x in pdf_segments]

    extraction_data = ExtractionData(tenant=task.tenant,
                                     pdf_file_name=task.pdf_file_name,
                                     paragraphs=segments)

    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)

    return extraction_data
