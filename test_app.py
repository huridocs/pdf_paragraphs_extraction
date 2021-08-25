import json
import os
import shutil

import mongomock as mongomock
import pymongo as pymongo
from fastapi.testclient import TestClient
from unittest import TestCase
from app import app
from data.ExtractionData import ExtractionData
from download_punkt import download_punkt

client = TestClient(app)

download_punkt()


class TestApp(TestCase):
    def test_info(self):
        response = client.get("/info")
        self.assertEqual(200, response.status_code)

    def test_error(self):
        response = client.get("/error")
        self.assertEqual(500, response.status_code)
        self.assertEqual({'detail': 'This is a test error from the error endpoint'}, response.json())

    def test_get_paragraphs(self):
        with open('test_files/test.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.get("/", files=files)
        extraction = json.loads(response.json())

        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(extraction['paragraphs']))
        self.assertEqual('A/INF/76/1', extraction['paragraphs'][0]['text'])
        self.assertEqual(612, extraction['page_width'])
        self.assertEqual(792, extraction['page_height'])
        self.assertEqual({1, 2}, {x['page_number'] for x in extraction['paragraphs']})

    def test_get_blank_pdf_paragraphs(self):
        with open('test_files/blank.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.get("/", files=files)
        extraction = json.loads(response.json())
        print(extraction)

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(extraction['paragraphs']))
        self.assertEqual(612, extraction['page_width'])
        self.assertEqual(792, extraction['page_height'])

    def test_add_task(self):
        shutil.rmtree('./docker_volume/to_segment/tenant_one', ignore_errors=True)

        with open('test_files/test.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.post("/async_extraction/tenant%20one", files=files)

        self.assertEqual('task registered', response.json())
        self.assertEqual(200, response.status_code)
        self.assertTrue(os.path.exists('./docker_volume/to_segment/tenant_one/test.pdf'))

        shutil.rmtree('./docker_volume/to_segment/tenant_one', ignore_errors=True)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_from_db(self):
        tenant = 'tenant_to_get_paragraphs'
        xml_file_name = 'xml_file_name'
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        json_data = [{'tenant': 'wrong tenant',
                      'xml_file_name': "wrong tenant",
                      'paragraphs_boxes': [],
                      }, {'tenant': tenant,
                          'xml_file_name': xml_file_name,
                          'paragraphs_boxes': [
                              {"left": 1, "top": 2, "width": 3, "height": 4, "page_number": 5, 'text': '1'},
                              {"left": 6, "top": 7, "width": 8, "height": 9, "page_number": 10, 'text': '2'}],
                          }, {'tenant': 'wrong tenant_2',
                              'xml_file_name': "wrong tenant",
                              'paragraphs_boxes': [],
                              }]

        mongo_client.pdf_paragraph.paragraphs.insert_many(json_data)

        response = client.get(f"/get_paragraphs/{tenant}/{xml_file_name}")

        extraction_data = ExtractionData(**json.loads(response.json()))

        self.assertEqual(200, response.status_code)
        self.assertEqual(tenant, extraction_data.tenant)
        self.assertEqual(xml_file_name, extraction_data.xml_file_name)
        self.assertEqual(2, len(extraction_data.paragraphs_boxes))
        self.assertEqual([1, 2, 3, 4, 5, '1'], list(extraction_data.paragraphs_boxes[0].dict().values()))
        self.assertEqual([6, 7, 8, 9, 10, '2'], list(extraction_data.paragraphs_boxes[1].dict().values()))
        self.assertIsNone(
            mongo_client.pdf_paragraph.paragraphs.find_one({"tenant": tenant, "xml_file_name": xml_file_name}))

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_paragraphs_when_no_data(self):
        tenant = 'tenant_to_get_paragraphs'
        xml_file_name = 'xml_file_name'

        response = client.get(f"/get_paragraphs/{tenant}/{xml_file_name}")

        self.assertEqual(404, response.status_code)
