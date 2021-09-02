import os
import shutil
from unittest import TestCase
from pdf_file.PdfFile import PdfFile

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
DOCKER_VOLUME_PATH = f'{ROOT_FOLDER}/docker_volume'

print(ROOT_FOLDER)


class TestPdfFile(TestCase):
    def test_save(self):
        tenant = 'tenant_one'
        pdf_file_name = 'test.pdf'
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

        pdf_file = PdfFile(tenant)
        with open(f'{ROOT_FOLDER}/test_files/test.pdf', 'rb') as file:
            pdf_file.save(pdf_file_name, file.read())

        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/tenant_one/test.pdf'))
        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

    def test_save_different_file(self):
        tenant = 'different_tenant_one'
        pdf_file_name = 'different_test.pdf'

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)

        pdf_file = PdfFile(tenant)
        with open(f'{ROOT_FOLDER}/test_files/test.pdf', 'rb') as file:
            pdf_file.save(pdf_file_name, file.read())

        self.assertTrue(os.path.exists(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}/{pdf_file_name}'))

        shutil.rmtree(f'{DOCKER_VOLUME_PATH}/to_extract/{tenant}', ignore_errors=True)
