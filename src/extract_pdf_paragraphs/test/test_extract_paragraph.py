import os
import shutil
from unittest import TestCase

import mongomock
import pymongo

from data.Params import Params
from data.Task import Task
from extract_pdf_paragraphs.extract_paragraphs import extract_paragraphs

ROOT_FOLDER = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
)
DOCKER_VOLUME_PATH = f"{ROOT_FOLDER}/docker_volume"


class TestGetParagraphs(TestCase):
    def test_extract_paragraphs(self):
        # setup
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"
        xml_file_name = "test.xml"
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)
        os.makedirs(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}")
        print(f"{ROOT_FOLDER}/extract_pdf_paragraph/test_files/test.pdf")
        shutil.copyfile(
            f"{ROOT_FOLDER}/src/test_files/test.pdf",
            f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}",
        )

        # act
        task = Task(
            tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name)
        )
        extraction_data = extract_paragraphs(task)

        # assert
        self.assertIsNotNone(extraction_data)
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(pdf_file_name, extraction_data.file_name)
        self.assertEqual(612, extraction_data.page_width)
        self.assertEqual(792, extraction_data.page_height)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual("A/INF/76/1", extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})
        self.assertTrue(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}")
        )
        self.assertFalse(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}")
        )

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)

    def test_extract_paragraphs_different_values(self):
        tenant = "different_tenant"
        pdf_file_name = "different_test.pdf"
        xml_file_name = "different_test.xml"
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)
        os.makedirs(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}")
        shutil.copyfile(
            f"{ROOT_FOLDER}/src/test_files/test.pdf",
            f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}",
        )

        task = Task(
            tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name)
        )

        extraction_data = extract_paragraphs(task)

        self.assertIsNotNone(extraction_data)
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(pdf_file_name, extraction_data.file_name)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual("A/INF/76/1", extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})

        self.assertTrue(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}")
        )
        self.assertFalse(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}")
        )

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)

    def test_extract_paragraphs_different_pdf(self):
        # setup
        tenant = "different_tenant"
        pdf_file_name = "different.pdf"
        xml_file_name = "different.xml"
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)
        os.makedirs(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}")
        shutil.copyfile(
            f"{ROOT_FOLDER}/src/test_files/different.pdf",
            f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}",
        )

        # act
        task = Task(
            tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name)
        )
        extraction_data = extract_paragraphs(task)

        # assert
        self.assertIsNotNone(extraction_data)
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(pdf_file_name, extraction_data.file_name)
        self.assertEqual(612, extraction_data.page_width)
        self.assertEqual(792, extraction_data.page_height)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual(12, len({x.page_number for x in extraction_data.paragraphs}))
        self.assertTrue(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/xml/{tenant}/{xml_file_name}")
        )
        self.assertFalse(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}")
        )

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)

    def test_extract_paragraphs_when_no_pdf_file(self):
        tenant = "test_extract_paragraphs_when_no_pdf_file"

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)

        os.makedirs(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}")
        task = Task(
            tenant=tenant, task="segmentation", params=Params(filename="no_file")
        )

        extraction_data = extract_paragraphs(task)

        self.assertIsNone(extraction_data)

    @mongomock.patch(servers=["mongodb://localhost:27017"])
    def test_extract_paragraphs_when_pdf_error(self):
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
        tenant = "tenant_async"
        pdf_file_name = "test.pdf"

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)

        os.makedirs(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}")
        shutil.copyfile(
            f"{ROOT_FOLDER}/README.md",
            f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}",
        )

        task = Task(
            tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name)
        )

        extract_paragraphs(task)

        self.assertIsNone(mongo_client.pdf_paragraph.paragraphs.find_one())
        self.assertFalse(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}")
        )
        self.assertFalse(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/xml/{tenant}/{pdf_file_name}")
        )
        self.assertTrue(
            os.path.exists(f"{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}/{pdf_file_name}")
        )

        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/to_extract/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/failed_pdf/{tenant}", ignore_errors=True)
        shutil.rmtree(f"{DOCKER_VOLUME_PATH}/xml/{tenant}", ignore_errors=True)
