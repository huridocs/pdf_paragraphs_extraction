import os
import pathlib

import config


class PdfFile:
    def __init__(self, tenant: str):
        self.tenant = tenant

    def save(self, pdf_file_name: str, file: bytes):
        if not os.path.exists(f"{config.DATA_PATH}/to_extract"):
            os.mkdir(f"{config.DATA_PATH}/to_extract")

        if not os.path.exists(f"{config.DATA_PATH}/to_extract/{self.tenant}"):
            os.mkdir(f"{config.DATA_PATH}/to_extract/{self.tenant}")

        path = f"{config.DATA_PATH}/to_extract/{self.tenant}/{pdf_file_name}"

        file_path_pdf = pathlib.Path(path)
        file_path_pdf.write_bytes(file)
