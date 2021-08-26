import json
import subprocess
from time import sleep
from unittest import TestCase

import requests

from data.ExtractionData import ExtractionData


class TestEndToEnd(TestCase):
    def test_end_to_end(self):
        tenant = 'end_to_end_test'
        pdf_file_name = 'test.pdf'
        host = 'http://localhost:5051'

        subprocess.run('docker-compose -f docker-compose-redis.yml up -d', shell=True)
        sleep(5)
        with open(f'test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        sleep(5)

        response = requests.get(f"{host}/get_paragraphs/{tenant}/{pdf_file_name}")

        extraction_data_dict = json.loads(response.json())
        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})

        subprocess.run('docker-compose -f docker-compose-redis.yml down', shell=True)
