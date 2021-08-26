import os
import pathlib
import datetime
from pathlib import Path

import pymongo

from data.Task import Task


class Tasks:
    def __init__(self, tenant: str):
        path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.root_folder = path.parent.absolute()
        self.tenant = tenant
        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        self.pdf_paragraph_db = client['pdf_paragraph']

    def add(self, pdf_file_name, file):
        if not os.path.exists(f'{self.root_folder}/docker_volume/to_extract'):
            os.mkdir(f'{self.root_folder}/docker_volume/to_extract')

        if not os.path.exists(f'{self.root_folder}/docker_volume/to_extract/{self.tenant}'):
            os.mkdir(f'{self.root_folder}/docker_volume/to_extract/{self.tenant}')

        path = f'{self.root_folder}/docker_volume/to_extract/{self.tenant}/{pdf_file_name}'

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
        task = Task(tenant=self.tenant, pdf_file_name=pdf_file_name)

        self.pdf_paragraph_db.tasks.delete_many({'tenant': task.tenant, 'pdf_file_name': pdf_file_name})
        self.pdf_paragraph_db.tasks.insert_one(task.dict())

    @classmethod
    def get_next_task(cls) -> Task:
        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        document = client['pdf_paragraph'].tasks.find_one_and_delete({})

        if not document:
            return None

        return Task(**document)
