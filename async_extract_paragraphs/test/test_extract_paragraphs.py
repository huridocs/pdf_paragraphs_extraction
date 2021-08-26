import datetime
import os
import shutil
from unittest import TestCase

import mongomock
import pymongo

from async_extract_paragraphs.extract_paragraphs_async import extract_paragraphs
from data.ExtractionData import ExtractionData
from data.Task import Task

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
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
        mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        extract_paragraphs()

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
    def test_extract_paragraphs_in_order(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')

        tenant_1 = "tenant_async_1"
        tenant_2 = "tenant_async_2"
        tenant_3 = "tenant_async_3"
        tenant_4 = "tenant_async_4"

        pdf_file_name = "test.pdf"
        xml_file_name = "test.xml"
        for tenant in [tenant_1, tenant_2]:
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
            os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
            shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                            f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        for tenant in [tenant_1, tenant_2, tenant_3, tenant_4]:
            task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
            mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        extract_paragraphs()
        extract_paragraphs()

        extraction_data_dict_1 = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_1, 'pdf_file_name': pdf_file_name})

        extraction_data_dict_2 = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_2, 'pdf_file_name': pdf_file_name})

        extraction_data_1 = ExtractionData(**extraction_data_dict_1)
        extraction_data_2 = ExtractionData(**extraction_data_dict_2)

        self.assertEqual(tenant_1, extraction_data_1.tenant)
        self.assertEqual(tenant_2, extraction_data_2.tenant)
        self.assertEqual(pdf_file_name, extraction_data_1.pdf_file_name)
        self.assertEqual(pdf_file_name, extraction_data_2.pdf_file_name)
        self.assertEqual('A/INF/76/1', extraction_data_1.paragraphs[0].text)
        self.assertEqual('A/INF/76/1', extraction_data_2.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data_1.paragraphs})
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data_2.paragraphs})

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_3, 'xml_file_name': xml_file_name}))
        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_4, 'xml_file_name': xml_file_name}))

        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant_1}/{xml_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant_2}/{xml_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

        for tenant in [tenant_1, tenant_2]:
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_extract_paragraphs_when_no_pdf_file(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        task = Task(tenant=tenant, pdf_file_name='no_file')
        mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        extract_paragraphs()

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
        mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        extract_paragraphs()

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
        mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        extract_paragraphs()

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        extract_paragraphs()

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
