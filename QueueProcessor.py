import os

import pymongo
import yaml
from pydantic import ValidationError
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ

from data.ExtractionMessage import ExtractionMessage

from data.Task import Task
from extract_pdf_paragraphs.extract_paragraphs_v2 import extract_paragraphs_v2
from get_logger import get_logger


class QueueProcessor:
    def __init__(self):
        self.logger = get_logger('redis_tasks')
        self.redis_host = 'redis_paragraphs'
        self.redis_port = 6379
        self.set_redis_parameters_from_yml()

        self.service_host = None
        self.service_port = None
        self.set_server_parameters_from_yml()

        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        self.pdf_paragraph_db = client['pdf_paragraph']

        self.extractions_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname='segmentation_results')
        self.extractions_queue.createQueue().exceptions(False).execute()

    def set_redis_parameters_from_yml(self):
        if not os.path.exists(f'config.yml'):
            return

        with open(f'config.yml', 'r') as f:
            config_dict = yaml.safe_load(f)
            self.redis_host = config_dict['redis_host'] if 'redis_host' in config_dict else self.redis_host
            self.redis_port = int(config_dict['redis_port']) if 'redis_port' in config_dict else self.redis_port

    def set_server_parameters_from_yml(self):
        if not os.path.exists(f'config.yml'):
            return

        with open(f'config.yml', 'r') as f:
            config_dict = yaml.safe_load(f)
            self.service_host = config_dict['service_host'] if 'service_host' in config_dict else self.service_host
            self.service_port = int(config_dict['service_port']) if 'service_port' in config_dict else self.service_port

    def process(self, id, message, rc, ts):
        try:
            task = Task(**message)
        except ValidationError:
            self.logger.error(f'Not a valid message: {message}')
            return True

        extraction_data = extract_paragraphs_v2(task)

        if not extraction_data:
            extraction_message = ExtractionMessage(tenant=task.tenant,
                                                   pdf_file_name=task.pdf_file_name,
                                                   success=False,
                                                   error_message='Error getting the xml from the pdf')

            self.extractions_queue.sendMessage().message(extraction_message.dict()).execute()
            self.logger.error(extraction_message.json())
            return True

        results_url = f'http://{self.service_host}:{self.service_port}/get_paragraphs/{task.tenant}/{task.pdf_file_name}'
        extraction_message = ExtractionMessage(tenant=extraction_data.tenant,
                                               pdf_file_name=extraction_data.pdf_file_name,
                                               success=True,
                                               results_url=results_url)

        self.pdf_paragraph_db.paragraphs.insert_one(extraction_data.dict())
        self.extractions_queue.sendMessage(delay=2).message(extraction_message.dict()).execute()
        return True

    def subscribe_to_extractions_tasks_queue(self):
        extractions_tasks_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname="segmentation_tasks")
        extractions_tasks_queue.createQueue().exceptions(False).execute()

        redis_smq_consumer = RedisSMQConsumer(qname="segmentation_tasks",
                                              processor=self.process,
                                              host=self.redis_host,
                                              port=self.redis_port)
        redis_smq_consumer.run()


if __name__ == '__main__':
    redis_tasks_processor = QueueProcessor()
    redis_tasks_processor.subscribe_to_extractions_tasks_queue()
