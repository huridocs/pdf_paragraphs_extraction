import json
import os

from fastapi.testclient import TestClient
from unittest import TestCase
from app import app

client = TestClient(app)


class TestApp(TestCase):
    def test_info(self):
        response = client.get("/info")
        self.assertEqual(200, response.status_code)

    def test_error(self):
        response = client.get("/error")
        self.assertEqual(500, response.status_code)
        self.assertEqual({'detail': 'This is a test error from the error endpoint'}, response.json())

    def test_segment(self):
        with open('test_pdf/test.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.get("/", files=files)
            segments_boxes = json.loads(response.json())
            pages = [segment_box['pageNumber'] for segment_box in segments_boxes['segments']]

            self.assertEqual(200, response.status_code)
            self.assertLess(15, len(segments_boxes['segments']))
            self.assertEqual('A/INF/76/1', segments_boxes['segments'][0]['text'])
            self.assertEqual(612, segments_boxes['pageWidth'])
            self.assertEqual(792, segments_boxes['pageHeight'])
            self.assertEqual(1, min(pages))
            self.assertEqual(2, max(pages))

    def test_blank_segment(self):
        with open('test_pdf/blank.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.get("/", files=files)
            segments_boxes = json.loads(response.json())

            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(segments_boxes['segments']))
            self.assertEqual(612, segments_boxes['pageWidth'])
            self.assertEqual(792, segments_boxes['pageHeight'])

    def test_add_task(self):
        with open('test_pdf/test.pdf', 'rb') as stream:
            files = {'file': stream}
            response = client.post("/add_task/tenant_one", files=files)
            self.assertEqual('task registered', response.json())
            self.assertEqual(200, response.status_code)
            self.assertTrue(os.path.exists('./docker_volume/to_segment/tenant_one/test.pdf'))
            os.remove('./docker_volume/to_segment/tenant_one/test.pdf')
            os.rmdir('./docker_volume/to_segment/tenant_one')