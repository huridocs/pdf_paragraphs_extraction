import datetime
import os
import shutil
from unittest import TestCase

import mongomock
import pymongo

from data.Task import Task
from tasks.Tasks import Tasks

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
DOCKER_VOLUME_PATH = f'{ROOT_FOLDER}/docker_volume'


class TestTasks(TestCase):
    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_add_task(self):
        tenant = 'tenant_one'
        pdf_file_name = 'test.pdf'
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')

        tasks = Tasks(tenant)
        with open(f'{ROOT_FOLDER}/test_files/test.pdf', 'rb') as file:
            tasks.add(pdf_file_name, file.read())

        document = mongo_client.pdf_paragraph.tasks.find_one({'tenant': tenant, 'pdf_file_name': pdf_file_name})
        task = Task(**document)

        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/tenant_one/test.pdf'))
        self.assertEqual(tenant, task.tenant)
        self.assertEqual(pdf_file_name, task.pdf_file_name)
        os.remove(f'{DOCKER_VOLUME_PATH}/to_extract/tenant_one/test.pdf')
        os.rmdir(f'{DOCKER_VOLUME_PATH}/to_extract/tenant_one')

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_add_same_task_twice(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        tenant = 'tenant_tasks'
        pdf_file_name = 'test.pdf'
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

        tasks = Tasks(tenant)
        with open(f'{ROOT_FOLDER}/test_files/test.pdf', 'rb') as file:
            tasks.add(pdf_file_name, file.read())
            tasks.add(pdf_file_name, file.read())

        documents = []
        for document in mongo_client.pdf_paragraph.tasks.find({'tenant': tenant, 'pdf_file_name': pdf_file_name}):
            documents.append(document)

        self.assertEqual(1, len(documents))
        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/test.pdf'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_next_task(self):
        mongo_client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')

        tenant = 'tenant_tasks'
        pdf_file_name = 'pdf_file_name_tasks'

        for i in range(10):
            task = Task(tenant=tenant+str(i), pdf_file_name=pdf_file_name+str(i))
            mongo_client.pdf_paragraph.tasks.insert_one(task.dict())

        task = Tasks.get_next_task()

        documents = []
        for document in mongo_client.pdf_paragraph.tasks.find({}):
            documents.append(document)

        self.assertEqual(9, len(documents))
        self.assertEqual(tenant + '0', task.tenant)
        self.assertEqual(pdf_file_name + '0', task.pdf_file_name)

    @mongomock.patch(servers=['mongodb://mongo_paragraphs:27017'])
    def test_get_next_task_should_return_none_when_no_tasks(self):
        task = Tasks.get_next_task()
        self.assertIsNone(task)