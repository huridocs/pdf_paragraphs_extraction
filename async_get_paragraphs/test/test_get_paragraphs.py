import os
import shutil
from unittest import TestCase

import mongomock
import pymongo

from async_get_paragraphs.get_paragraphs_loop import get_paragraphs
from data.ExtractionData import ExtractionData

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
DOCKER_VOLUME_PATH = f'{ROOT_FOLDER}/docker_volume'


class TestGetParagraphs(TestCase):

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"
        xml_file_name = "test.xml"
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                        f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()

        extraction_data_dict = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant, 'xml_file_name': xml_file_name})

        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(xml_file_name, extraction_data.xml_file_name)
        self.assertLess(15, len(extraction_data.paragraphs_boxes))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs_boxes[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs_boxes})
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_two_tenants(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant_1 = "tenant_async_1"
        tenant_2 = "tenant_async_2"
        pdf_file_name = "test.pdf"
        xml_file_name = "test.xml"
        for tenant in [tenant_1, tenant_2]:
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
            shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
            os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
            shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                            f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()
        get_paragraphs()

        extraction_data_dict_1 = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_1, 'xml_file_name': xml_file_name})

        extraction_data_dict_2 = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant_2, 'xml_file_name': xml_file_name})

        extraction_data_1 = ExtractionData(**extraction_data_dict_1)
        extraction_data_2 = ExtractionData(**extraction_data_dict_2)

        self.assertEqual(tenant_1, extraction_data_1.tenant)
        self.assertEqual(tenant_2, extraction_data_2.tenant)
        self.assertEqual(xml_file_name, extraction_data_1.xml_file_name)
        self.assertEqual(xml_file_name, extraction_data_2.xml_file_name)
        self.assertEqual('A/INF/76/1', extraction_data_1.paragraphs_boxes[0].text)
        self.assertEqual('A/INF/76/1', extraction_data_2.paragraphs_boxes[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data_1.paragraphs_boxes})
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data_2.paragraphs_boxes})
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant_1}/{xml_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant_2}/{xml_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_when_no_pdf_file(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/README.md')

        get_paragraphs()

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_when_pdf_uppercase(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.PdF"
        xml_file_name = "test.xml"
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/test_files/test.pdf',
                        f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()

        extraction_data_dict = mongo_client.pdf_paragraph.paragraphs.find_one(
            {'tenant': tenant, 'xml_file_name': xml_file_name})

        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertIsNotNone(extraction_data)
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_when_pdf_error(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_when_twice_pdf_error(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)

        os.makedirs(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}')
        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()

        shutil.copyfile(f'{ROOT_FOLDER}/README.md', f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}')

        get_paragraphs()

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))
        self.assertFalse(os.path.exists(f'{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}'))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}', ignore_errors=True)
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/xml/{tenant}', ignore_errors=True)
