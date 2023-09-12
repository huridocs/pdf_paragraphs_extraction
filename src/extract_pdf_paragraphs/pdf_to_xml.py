import os
import uuid
from pathlib import Path

import config

THIS_SCRIPT_PATH = Path(__file__).parent.absolute()


def get_file_path(file_name, extension):
    if not os.path.exists(f"{config.DATA_PATH}/files"):
        os.makedirs(f"{config.DATA_PATH}/files")

    if not os.path.exists(f"{config.DATA_PATH}/files/{extension}"):
        os.makedirs(f"{config.DATA_PATH}/files/{extension}")

    return f"{config.DATA_PATH}/files/{extension}/{file_name}.{extension}"


def pdf_content_to_pdf_path(file_content):
    file_id = str(uuid.uuid1())

    pdf_path = Path(get_file_path(file_id, "pdf"))
    pdf_path.write_bytes(file_content)

    return pdf_path
