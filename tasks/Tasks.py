import os
import pathlib
from pathlib import Path


class Tasks:
    def __init__(self, tenant: str = None):
        path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.root_folder = path.parent.absolute()
        self.tenant = tenant

    def add(self, filename, file):
        if self.tenant:
            if not os.path.exists(f'{self.root_folder}/docker_volume/to_segment/{self.tenant}'):
                os.mkdir(f'{self.root_folder}/docker_volume/to_segment/{self.tenant}')

            path = f'{self.root_folder}/docker_volume/to_segment/{self.tenant}/{filename}'
        else:
            path = f'{self.root_folder}/docker_volume/to_segment/{filename}'

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
