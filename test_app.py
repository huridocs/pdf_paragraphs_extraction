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
        files = {'file': open('test_pdf/test_pdf.pdf', 'rb')}
        response = client.post("/", files=files)
        print(response.json())
        segments_boxes = json.loads(response.json())
        pages = [segment_box['pageNumber'] for segment_box in segments_boxes]

        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(segments_boxes))
        self.assertEqual(1, min(pages))
        self.assertEqual(2, max(pages))

    def test_add_segmentation_task(self):
        files = {'file': open('test_pdf/test_pdf.pdf', 'rb')}
        response = client.post("/add_segmentation_task", files=files)
        self.assertEqual(200, response.status_code)
        self.assertEqual('task registered', response.json())
        self.assertTrue(os.path.exists('./docker_volume/to_segment/test_pdf.pdf'))
        os.remove('./docker_volume/to_segment/test_pdf.pdf')
