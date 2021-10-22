import os
from time import sleep

import pymongo
import redis
import yaml
from pydantic import ValidationError
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ

from data.ExtractionMessage import ExtractionMessage

from data.Task import Task
from extract_pdf_paragraphs.extract_paragraphs import extract_paragraphs
from get_logger import get_logger


class QueueProcessor:
    def __init__(self):
        self.logger = get_logger('redis_tasks')
        self.redis_host = 'redis_paragraphs'
        self.redis_port = 6379
        self.set_redis_parameters_from_yml()

        self.service_url = 'http://localhost:5051'
        self.set_server_parameters_from_yml()

        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        self.pdf_paragraph_db = client['pdf_paragraph']

        self.results_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname='segmentation_results')

    def set_redis_parameters_from_yml(self):
        if not os.path.exists(f'config.yml'):
            return

        with open(f'config.yml', 'r') as f:
            config_dict = yaml.safe_load(f)
            if not config_dict:
                return

            self.redis_host = config_dict['redis_host'] if 'redis_host' in config_dict else self.redis_host
            self.redis_port = int(config_dict['redis_port']) if 'redis_port' in config_dict else self.redis_port

    def set_server_parameters_from_yml(self):
        if not os.path.exists(f'config.yml'):
            return

        with open(f'config.yml', 'r') as f:
            config_dict = yaml.safe_load(f)
            if not config_dict:
                return

            service_host = config_dict['service_host'] if 'service_host' in config_dict else 'localhost'
            service_port = int(config_dict['service_port']) if 'service_port' in config_dict else 5051
            self.service_url = f'http://{service_host}:{service_port}'

    def process(self, id, message, rc, ts):
        try:
            task = Task(**message)
        except ValidationError:
            self.logger.error(f'Not a valid message: {message}')
            return True

        self.logger.error(f'Valid message: {message}')

        try:
            extraction_data = extract_paragraphs(task)

            if not extraction_data:
                extraction_message = ExtractionMessage(tenant=task.tenant,
                                                       task=task.task,
                                                       params=task.params,
                                                       success=False,
                                                       error_message='Error getting the xml from the pdf')

                self.results_queue.sendMessage().message(extraction_message.dict()).execute()
                self.logger.error(extraction_message.json())
                return True

            results_url = f'{self.service_url}/get_paragraphs/{task.tenant}/{task.params.filename}'
            file_results_url = f'{self.service_url}/get_xml/{task.tenant}/{task.params.filename}'
            extraction_message = ExtractionMessage(tenant=extraction_data.tenant,
                                                   task=task.task,
                                                   params=task.params,
                                                   success=True,
                                                   data_url=results_url,
                                                   file_url=file_results_url)

            self.pdf_paragraph_db.paragraphs.insert_one(extraction_data.dict())
            self.logger.info(extraction_message.json())
            self.results_queue.sendMessage(delay=3).message(extraction_message.dict()).execute()
            return True
        except Exception:
            self.logger.error('error', exc_info=1)
            return True

    def subscribe_to_extractions_tasks_queue(self):
        while True:
            try:
                self.results_queue.createQueue().vt(120).exceptions(False).execute()
                extractions_tasks_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname="segmentation_tasks")
                extractions_tasks_queue.createQueue().vt(120).exceptions(False).execute()

                self.logger.info(f'Connecting to redis: {self.redis_host}:{self.redis_port}')

                redis_smq_consumer = RedisSMQConsumer(qname="segmentation_tasks",
                                                      processor=self.process,
                                                      host=self.redis_host,
                                                      port=self.redis_port)
                redis_smq_consumer.run()
            except redis.exceptions.ConnectionError:
                self.logger.error(f'Error connecting to redis: {self.redis_host}:{self.redis_port}')
                sleep(20)


if __name__ == '__main__':
    redis_tasks_processor = QueueProcessor()
    redis_tasks_processor.subscribe_to_extractions_tasks_queue()
