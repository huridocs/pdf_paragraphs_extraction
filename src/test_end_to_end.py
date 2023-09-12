import json
import time
from unittest import TestCase

import requests
from rsmq import RedisSMQ

import config
from data.ExtractionData import ExtractionData
from data.ExtractionMessage import ExtractionMessage
from data.Params import Params
from data.Task import Task


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5051"

    def test_error_file(self):
        tenant = "end_to_end_test_error"
        pdf_file_name = "error_pdf.pdf"
        queue = RedisSMQ(host="127.0.0.1", port="6379", qname="segmentation_tasks")

        with open(f"{config.APP_PATH}/test_files/error_pdf.pdf", "rb") as stream:
            files = {"file": stream}
            requests.post(f"{self.service_url}/async_extraction/{tenant}", files=files)

        task = Task(tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name))

        queue.sendMessage().message(task.model_dump_json()).execute()

        extraction_message = self.get_redis_message()

        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual("error_pdf.pdf", extraction_message.params.filename)
        self.assertEqual(False, extraction_message.success)

    def test_async_extraction(self):
        tenant = "end_to_end_test"
        pdf_file_name = "test.pdf"

        with open(f"{config.APP_PATH}/test_files/{pdf_file_name}", "rb") as stream:
            files = {"file": stream}
            requests.post(f"{self.service_url}/async_extraction/{tenant}", files=files)

        queue = RedisSMQ(host="127.0.0.1", port="6379", qname="segmentation_tasks")

        queue.sendMessage().message('{"message_to_avoid":"to_be_written_in_log_file"}').execute()

        task = Task(tenant=tenant, task="segmentation", params=Params(filename=pdf_file_name))
        queue.sendMessage().message(str(task.model_dump_json())).execute()

        extraction_message = self.get_redis_message()

        response = requests.get(extraction_message.data_url)

        extraction_data_dict = json.loads(response.json())
        extraction_data = ExtractionData(**extraction_data_dict)

        self.assertEqual(tenant, extraction_message.tenant)
        self.assertEqual(pdf_file_name, extraction_message.params.filename)
        self.assertEqual(True, extraction_message.success)
        self.assertEqual(200, response.status_code)
        self.assertLess(15, len(extraction_data.paragraphs))
        self.assertEqual(612, extraction_data.page_width)
        self.assertEqual(792, extraction_data.page_height)
        self.assertEqual("United Nations", extraction_data.paragraphs[0].text)
        self.assertEqual({1, 2}, {x.page_number for x in extraction_data.paragraphs})

        response = requests.get(extraction_message.file_url)
        self.assertEqual(200, response.status_code)
        self.assertTrue('<?xml version="1.0" encoding="UTF-8"?>' in str(response.content))

    def test_blank_pdf(self):
        with open(f"{config.APP_PATH}/test_files/blank.pdf", "rb") as stream:
            files = {"file": stream}
            response = requests.post(f"{self.service_url}", files=files)

        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['page_height'], 792)
        self.assertEqual(response_json['page_width'], 612)
        self.assertEqual(response_json['paragraphs'], [])

    def test_one_token_per_page_pdf(self):
        with open(f"{config.APP_PATH}/test_files/one_token_per_page.pdf", "rb") as stream:
            files = {"file": stream}
            response = requests.post(f"{self.service_url}", files=files)

        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json['paragraphs']), 2)
        self.assertEqual(response_json['paragraphs'][0]['page_number'], 1)
        self.assertEqual(response_json['paragraphs'][1]['page_number'], 2)

    @staticmethod
    def get_redis_message() -> ExtractionMessage:
        queue = RedisSMQ(host="127.0.0.1", port="6379", qname="segmentation_results", quiet=True)

        for i in range(80):
            time.sleep(0.5)
            message = queue.receiveMessage().exceptions(False).execute()
            if message:
                queue.deleteMessage(id=message["id"]).execute()
                return ExtractionMessage(**json.loads(message["message"]))
