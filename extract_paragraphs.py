import json
import os
import typing

import pymongo
import yaml
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ

from data.ExtractionMessage import ExtractionMessage
from extract_pdf_paragraphs.information_extraction.InformationExtraction import InformationExtraction

from data.Task import Task
from data.ExtractionData import ExtractionData


ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DOCKER_VOLUME = f'{ROOT_DIRECTORY}/docker_volume'

if os.path.exists(f'{DOCKER_VOLUME}/redis_server.yml'):
    REDIS_SERVER = yaml.safe_load(open(f'{DOCKER_VOLUME}/redis_server.yml', 'r'))['host']
    REDIS_PORT = int(yaml.safe_load(open(f'{DOCKER_VOLUME}/redis_server.yml', 'r'))['port'])
else:
    REDIS_SERVER = 'redis_paragraphs'
    REDIS_PORT = 6379


def get_paths(tenant: str, pdf_file_name: str):
    file_name = ''.join(pdf_file_name.split('.')[:-1])
    pdf_file_path = f'{DOCKER_VOLUME}/to_extract/{tenant}/{pdf_file_name}'
    xml_file_path = f'{DOCKER_VOLUME}/xml/{tenant}/{file_name}.xml'
    failed_pdf_path = f'{DOCKER_VOLUME}/failed_pdf/{tenant}/{pdf_file_name}'
    return pdf_file_path, xml_file_path, failed_pdf_path


def extract_paragraphs(task: Task) -> typing.Optional[ExtractionMessage]:
    pdf_file_path, xml_file_path, failed_pdf_path = get_paths(task.tenant, task.pdf_file_name)
    information_extraction = InformationExtraction.from_pdf_path(pdf_path=pdf_file_path,
                                                                 xml_file_path=xml_file_path,
                                                                 failed_pdf_path=failed_pdf_path)

    if not information_extraction:
        return ExtractionMessage(tenant=task.tenant,
                                 pdf_file_name=task.pdf_file_name,
                                 success=False,
                                 error_message='Error getting the xml from the pdf')

    extraction_data = ExtractionData.from_segments(tenant=task.tenant,
                                                   pdf_file_name=task.pdf_file_name,
                                                   segments=information_extraction.segments)

    client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
    client['pdf_paragraph'].paragraphs.insert_one(extraction_data.dict())
    os.remove(pdf_file_path)

    return ExtractionMessage(tenant=task.tenant,
                             pdf_file_name=task.pdf_file_name,
                             success=True,
                             error_message='')


def process(id, message, rc, ts):
    print('processsing :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')
    print(message)
    task_dict = json.loads(message)
    task = Task(**task_dict)
    print('task created :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::')

    extraction_message = extract_paragraphs(task)
    if extraction_message:
        queue = RedisSMQ(host=REDIS_SERVER, port=REDIS_PORT, qname="extractions")
        queue.createQueue().exceptions(False).execute()
        queue.sendMessage().message(extraction_message.dict()).execute()

    return True


if __name__ == '__main__':
    print('starting RedisSMQConsumerThread')
    queue = RedisSMQ(host=REDIS_SERVER, port=REDIS_PORT, qname="extractions_tasks")
    queue.createQueue().exceptions(False).execute()
    redis_smq_consumer = RedisSMQConsumer(qname="extractions_tasks",
                                                processor=process,
                                                host=REDIS_SERVER,
                                                port=REDIS_PORT)
    redis_smq_consumer.run()
    print('started RedisSMQConsumerThread')

