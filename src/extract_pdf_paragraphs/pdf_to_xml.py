import os
import pathlib
import uuid

import config

THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def get_file_path(file_name, extension):
    if not os.path.exists(f"{config.DATA_PATH}/files_pdfalto"):
        os.makedirs(f"{config.DATA_PATH}/files_pdfalto")

    if not os.path.exists(f"{config.DATA_PATH}/files_pdfalto/{extension}"):
        os.makedirs(f"{config.DATA_PATH}/files_pdfalto/{extension}")

    return f"{config.DATA_PATH}/files_pdfalto/{extension}/{file_name}.{extension}"


def pdf_content_to_pdf_path(file_content):
    file_id = str(uuid.uuid1())

    pdf_path = pathlib.Path(get_file_path(file_id, "pdf"))
    pdf_path.write_bytes(file_content)

    return pdf_path
