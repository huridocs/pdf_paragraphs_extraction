import os
import pathlib
from pathlib import Path


class PdfFile:
    def __init__(self, tenant: str):
        path = Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.root_folder = path.parent.absolute()
        self.tenant = tenant

    def save(self, pdf_file_name: str, file: bytes):
        if not os.path.exists(f"{self.root_folder}/docker_volume/to_extract"):
            os.mkdir(f"{self.root_folder}/docker_volume/to_extract")

        if not os.path.exists(
            f"{self.root_folder}/docker_volume/to_extract/{self.tenant}"
        ):
            os.mkdir(f"{self.root_folder}/docker_volume/to_extract/{self.tenant}")

        path = (
            f"{self.root_folder}/docker_volume/to_extract/{self.tenant}/{pdf_file_name}"
        )

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
