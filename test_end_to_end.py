import json
import os
import shutil
import subprocess
import time
from unittest import TestCase

import requests
from rsmq import RedisSMQ

from config_creator import create_configuration
from data.ExtractionData import ExtractionData
from data.ExtractionMessage import ExtractionMessage
from data.Task import Task


class TestEndToEnd(TestCase):
    def setUp(self):
        create_configuration()
        subprocess.run('docker-compose -f docker-compose-service-with-redis.yml up  -d', shell=True)
        time.sleep(5)

    def tearDown(self):
        subprocess.run('docker-compose -f docker-compose-service-with-redis.yml down', shell=True)

    def test_end_to_end(self):
        root_path = '.'
        docker_volume_path = f'{root_path}/docker_volume'

        tenant = 'end_to_end_test'
        pdf_file_name = 'test.pdf'
        host = 'http://localhost:5051'

        with open(f'{root_path}/test_files/{pdf_file_name}', 'rb') as stream:
            files = {'file': stream}
            requests.post(f"{host}/async_extraction/{tenant}", files=files)

        queue = RedisSMQ(host='127.0.0.1', port='6479', qname="segmentation_tasks")
        task = Task(tenant=tenant, pdf_file_name=pdf_file_name)

        queue.sendMessage().message('{"message_to_avoid":"to_write_in_log"}').execute()

        queue.sendMessage().message(str(task.json())).execute()

        extraction_message = self.get_redis_message()

        response = requests.get(extraction_message.results_url)

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

    @staticmethod
    def get_redis_message() -> ExtractionMessage:
        queue = RedisSMQ(host='127.0.0.1', port='6479', qname='segmentation_results', quiet=True)

        for i in range(10):
            time.sleep(2)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                queue.deleteMessage(id=message['id']).execute()
                return ExtractionMessage(**json.loads(message['message']))
