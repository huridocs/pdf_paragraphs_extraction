import json
import os
from time import sleep

import pymongo
import yaml
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ

from data.ExtractionMessage import ExtractionMessage
from extract_pdf_paragraphs.extract_paragraphs import extract_paragraphs

from data.Task import Task
from get_logger import get_logger


class RedisTasksProcessor:
    def __init__(self):
        root_directory = os.path.dirname(os.path.realpath(__file__))
        self.docker_volume_path = f'{root_directory}/docker_volume'
        self.logger = get_logger('redis_tasks')
        self.logger.info('RedisTasksProcessor')
        self.redis_host = 'redis_paragraphs'
        self.redis_port = 6379
        self.set_redis_parameters_from_yml()

        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        self.pdf_paragraph_db = client['pdf_paragraph']

        self.extractions_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname="extractions")
        self.extractions_queue.createQueue().exceptions(False).execute()

    def set_redis_parameters_from_yml(self):
        if os.path.exists(f'{self.docker_volume_path}/redis_server.yml'):
            self.redis_host = yaml.safe_load(open(f'{self.docker_volume_path}/redis_server.yml', 'r'))['host']
            self.redis_port = int(yaml.safe_load(open(f'{self.docker_volume_path}/redis_server.yml', 'r'))['port'])

    def process(self, id, message, rc, ts):
        task = Task(**message)

        extraction_data = extract_paragraphs(task)

        if not extraction_data:
            extraction_message = ExtractionMessage(tenant=task.tenant,
                              pdf_file_name=task.pdf_file_name,
                              success=False,
                              error_message='Error getting the xml from the pdf')

            self.extractions_queue.sendMessage().message(extraction_message.dict()).execute()
            self.logger.error(extraction_message.json())
            return True

        extraction_message = ExtractionMessage(tenant=extraction_data.tenant,
                                               pdf_file_name=extraction_data.pdf_file_name,
                                               success=True,
                                               error_message='')
        self.logger.error(str(extraction_data.dict()))
        self.pdf_paragraph_db.paragraphs.insert_one(extraction_data.dict())
        sleep(0.5)
        self.extractions_queue.sendMessage().message(extraction_message.dict()).execute()
        return True

    def subscribe_to_extractions_tasks_queue(self):
        extractions_tasks_queue = RedisSMQ(host=self.redis_host, port=self.redis_port, qname="extractions_tasks")
        extractions_tasks_queue.createQueue().exceptions(False).execute()

        redis_smq_consumer = RedisSMQConsumer(qname="extractions_tasks",
                                              processor=self.process,
                                              host=self.redis_host,
                                              port=self.redis_port)
        redis_smq_consumer.run()


if __name__ == '__main__':
    redis_tasks_processor = RedisTasksProcessor()
    redis_tasks_processor.subscribe_to_extractions_tasks_queue()
