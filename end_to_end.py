import json
import os
import shutil
import subprocess
import time
from unittest import TestCase

import requests
from rsmq import RedisSMQ

from data.ExtractionData import ExtractionData
from data.ExtractionMessage import ExtractionMessage
from data.Task import Task


class TestEndToEnd(TestCase):

    def test_end_to_end(self):
        root_path = '.'
        docker_volume_path = f'{root_path}/docker_volume'

        tenant = 'end_to_end_test'
        pdf_file_name = 'test.pdf'
        host = 'http://localhost:5050'

        subprocess.run('docker-compose up -d', shell=True)
        time.sleep(5)

        result = requests.get(f"{host}/info")
        self.assertEqual(200, result.status_code)

        with open(f'{root_path}/test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="extractions_tasks")
        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        queue.sendMessage().message(str(task.json())).execute()

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

        shutil.rmtree(f'{docker_volume_path}/xml/{tenant}', ignore_errors=True)

        tenant = 'end_to_end_test_error'
        pdf_file_name = 'README.md'

        with open(f'{root_path}/README.md', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)
        queue.sendMessage().message(task.json()).execute()

        extraction_message = self.get_redis_message()

        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual('README.md', extraction_message.pdf_file_name)
        self.assertEqual(False, extraction_message.success)
        self.assertTrue(os.path.exists(
            f'{docker_volume_path}/failed_pdf/{extraction_message.tenant}/{extraction_message.pdf_file_name}'))

        shutil.rmtree(f'{docker_volume_path}/failed_pdf/{tenant}', ignore_errors=True)
        subprocess.run('docker-compose down', shell=True)

    @staticmethod
    def get_redis_message():
        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="extractions", quiet=True)

        for i in range(10):
            time.sleep(2)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                queue.deleteMessage(id=message['id']).execute()
                return ExtractionMessage(**json.loads(message['message']))
