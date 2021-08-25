import asyncio
import os

import pymongo

from data.ExtractionData import ExtractionData
from information_extraction.InformationExtraction import InformationExtraction

ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKER_VOLUME = f'{ROOT_DIRECTORY}/docker_volume'


def get_paths(tenant: str, pdf_file_name: str):
    file_name = ''.join(pdf_file_name.split('.')[:-1])
    pdf_file_path = f'{DOCKER_VOLUME}/to_extract/{tenant}/{pdf_file_name}'
    xml_file_path = f'{DOCKER_VOLUME}/xml/{tenant}/{file_name}.xml'
    failed_pdf_path = f'{DOCKER_VOLUME}/failed_pdf/{tenant}/{pdf_file_name}'
    return pdf_file_path, xml_file_path, failed_pdf_path


def get_paragraphs():
    for tenant_folder in os.listdir(f'{DOCKER_VOLUME}/to_extract'):
        for pdf_file_name in os.listdir(f'{DOCKER_VOLUME}/to_extract/{tenant_folder}'):
            if '.pdf' not in pdf_file_name.lower():
                continue
            pdf_file_path, xml_file_path, failed_pdf_path = get_paths(tenant_folder, pdf_file_name)
            information_extraction = InformationExtraction.from_pdf_path(pdf_path=pdf_file_path,
                                                                         xml_file_path=xml_file_path,
                                                                         failed_pdf_path=failed_pdf_path)

            if not information_extraction:
                return

            extraction_data = ExtractionData.from_segments(tenant=tenant_folder,
                                                           xml_file_name=xml_file_path.split('/')[-1],
                                                           segments=information_extraction.segments)

            client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
            client['pdf_paragraph'].paragraphs.insert_one(extraction_data.dict())
            os.remove(pdf_file_path)
            return


async def get_paragraphs_async():
    get_paragraphs()
    await asyncio.sleep(1)


def loop_calculate_suggestions():
    while True:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_paragraphs_async())


if __name__ == '__main__':
    loop_calculate_suggestions()
