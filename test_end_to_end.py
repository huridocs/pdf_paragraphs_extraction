import json
import os
import shutil
import time
from unittest import TestCase

import requests
from rsmq import RedisSMQ

from data.ExtractionData import ExtractionData
from data.ExtractionMessage import ExtractionMessage
from data.Task import Task


class TestEndToEnd(TestCase):

    def test_end_to_end(self):
        tenant = 'end_to_end_test'
        pdf_file_name = 'test.pdf'
        host = 'http://localhost:5051'

        # subprocess.run('docker-compose -f docker-compose.yml up -d', shell=True)
        # sleep(5)

        with open(f'test_files/{pdf_file_name}', 'rb') as stream:
            files = {'pdf_file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="extractions_tasks")
        queue.createQueue().exceptions(False).execute()
        queue.sendMessage().message(task.json())

        extraction_message = self.get_redis_message()

        response = requests.get(
            f"{host}/get_paragraphs/{extraction_message.tenant}/{extraction_message.pdf_file_name}")

        extraction_data_dict = json.loads(response.json())
        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual(pdf_file_name, extraction_message.pdf_file_name)
        self.assertEqual(True, extraction_message.success)
        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual('A/INF/76/1', extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})

        shutil.rmtree(f'./docker_volume/xml/{tenant}', ignore_errors=True)

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)

        self.queue.sendMessage().message(task.json())

        tenant = 'end_to_end_error'
        with open('README.md', 'rb') as stream:
            files = {'pdf_file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        extraction_message = self.get_redis_message()
        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual('README.md', extraction_message.pdf_file_name)
        self.assertEqual(False, extraction_message.success)
        self.assertTrue(os.path.exists(f'./docker_volume/failed_pdf/{tenant}/README.md'))

        shutil.rmtree(f'./docker_volume/failed_pdf/{tenant}', ignore_errors=True)
        # subprocess.run('docker-compose -f docker-compose.yml down', shell=True)

    @staticmethod
    def get_redis_message():
        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="extractions", quiet=True)
        queue.createQueue().exceptions(False).execute()

        for i in range(10):
            time.sleep(2)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                return ExtractionMessage(**json.loads(message['message']))
            else:
                print('nothing')