import os
import shutil
import sys
from unittest import TestCase

import mongomock
import pymongo

from data.ExtractionData import ExtractionData
from data.Task import Task

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from extract_paragraphs import extract_paragraphs


ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DOCKER_VOLUME_PATH = f'{ROOT_FOLDER}/docker_volume'


class TestGetParagraphs(TestCase):
    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"
        xml_file_name = "test.xml"
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                        f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        extract_paragraphs(task)

        extraction_data_dict = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant, 'pdf_file_name': pdf_file_name})

        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertIsNone(mongo_client.pdf_paragraph.tasks.find_one())
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(pdf_file_name, extraction_data.pdf_file_name)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs_different_values(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "different_tenant"
        pdf_file_name = "different_test.pdf"
        xml_file_name = "different_test.xml"
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                        f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        extract_paragraphs(task)

        extraction_data_dict = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant, 'pdf_file_name': pdf_file_name})

        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertIsNone(mongo_client.pdf_paragraph.tasks.find_one())
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(pdf_file_name, extraction_data.pdf_file_name)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs_when_no_pdf_file(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        task = Task(tenant=tenant, pdf_file_name='no_file')
        extract_paragraphs(task)

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertIsNone(mongo_client.pdf_paragraph.tasks.find_one())

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs_when_pdf_error(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        extract_paragraphs(task)

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs_when_twice_pdf_error(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)

        extract_paragraphs(task)

        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')
        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)

        extract_paragraphs(task)

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
