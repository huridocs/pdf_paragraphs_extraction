import json
import os
import shutil
import subprocess
import time
from time import sleep
from unittest import TestCase

import requests
from rsmq import RedisSMQ

from data.ExtractionData import ExtractionData
from data.ExtractionMessage import ExtractionMessage


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

        extraction_message = self.get_redis_message()

        response = requests.get(
            f"{host}/get_paragraphs/{extraction_message.tenant}/{extraction_message.pdf_file_name}")

        extraction_data_dict = json.loads(response.json())
        extraction_data = ExtractionData(**extraction_data_dict)
        print(extraction_message.json())

        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual(pdf_file_name, extraction_message.pdf_file_name)
        self.assertEqual(True, extraction_message.success)
        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})

        shutil.rmtree(f'./docker_volume/xml/{tenant}', ignore_errors=True)

        tenant = 'end_to_end_error'
        with open('README.md', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        extraction_message = self.get_redis_message()
        print(extraction_message.json())
        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual('README.md', extraction_message.pdf_file_name)
        self.assertEqual(False, extraction_message.success)
        self.assertTrue(os.path.exists(f'./docker_volume/failed_pdf/{tenant}/README.md'))

        shutil.rmtree(f'./docker_volume/failed_pdf/{tenant}', ignore_errors=True)
        subprocess.run('docker-compose -f docker-compose-redis.yml down', shell=True)

    @staticmethod
    def get_redis_message():
        extraction_message = ExtractionMessage(tenant='', pdf_file_name='', success=False)
        for i in range(10):
            time.sleep(1)
            queue = RedisSMQ(host='127.0.0.1', port='6479', qname="paragraphs_extraction", quiet=True)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                extraction_message = ExtractionMessage(**json.loads(message['message']))
        return extraction_message
