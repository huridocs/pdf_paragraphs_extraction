import os
import shutil
import typing

from data.ExtractionMessage import ExtractionMessage
from extract_pdf_paragraphs.information_extraction.InformationExtraction import InformationExtraction

from data.Task import Task
from data.ExtractionData import ExtractionData


ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKER_VOLUME = f'{ROOT_DIRECTORY}/docker_volume'


def get_paths(tenant: str, pdf_file_name: str):
    file_name = ''.join(pdf_file_name.split('.')[:-1])
    pdf_file_path = f'{DOCKER_VOLUME}/to_extract/{tenant}/{pdf_file_name}'
    xml_file_path = f'{DOCKER_VOLUME}/xml/{tenant}/{file_name}.xml'
    failed_pdf_path = f'{DOCKER_VOLUME}/failed_pdf/{tenant}/{pdf_file_name}'
    return pdf_file_path, xml_file_path, failed_pdf_path


def extract_paragraphs(task: Task) -> typing.Optional[ExtractionData]:
    pdf_file_path, xml_file_path, failed_pdf_path = get_paths(task.tenant, task.pdf_file_name)
    information_extraction = InformationExtraction.from_pdf_path(pdf_path=pdf_file_path,
                                                                 xml_file_path=xml_file_path,
                                                                 failed_pdf_path=failed_pdf_path)

    if not information_extraction:
        return None

    extraction_data = ExtractionData.from_segments(tenant=task.tenant,
                                                   pdf_file_name=task.pdf_file_name,
                                                   segments=information_extraction.segments)

    if os.path.exists(pdf_file_path):
        os.remove(pdf_file_path)

    return extraction_data


