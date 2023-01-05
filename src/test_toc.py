import json
from unittest import TestCase

import requests

import config


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5051"

    def test_toc(self):
        with open(f"{config.APP_PATH}/test_files/toc-test.pdf", "rb") as stream:
            files = {"file": stream}
            response = requests.post(f"{self.service_url}/get_toc", files=files)

        toc = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(toc))
        self.assertEqual(
            {
                "indentation": 0,
                "label": "A. TITLE LONGER",
                "selectionRectangles": [{"left": 120, "top": 197, "width": 178, "height": 14, "page": "2"}],
            },
            toc[0],
        )

    def test_blank_pdf(self):
        with open(f"{config.APP_PATH}/test_files/blank.pdf", "rb") as stream:
            files = {"file": stream}
            response = requests.post(f"{self.service_url}/get_toc", files=files)

        toc = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], toc)

    def test_fail_toc(self):
        with open(f"{config.APP_PATH}/test_files/error_pdf.pdf", "rb") as stream:
            files = {"file": stream}
            response = requests.post(f"{self.service_url}/get_toc", files=files)

        self.assertEqual(422, response.status_code)
