import os
import shutil
import pathlib
import subprocess
import uuid

from lxml import etree
from lxml.etree import ElementBase
from pdf_features.PdfFeatures import PdfFeatures

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


def get_xml_from_file_content(file_content):
    file_id = str(uuid.uuid1())

    file_path_pdf = pathlib.Path(get_file_path(file_id, "pdf"))
    file_path_pdf.write_bytes(file_content)

    file_path_xml = get_file_path(file_id, "xml")
    file_xml_metadata_path = file_path_xml.replace(".xml", "_metadata.xml")
    file_xml_data_path = file_path_xml.replace(".xml", ".xml_data")

    create_xml_from_pdf(file_path_pdf, file_path_xml)

    with open(file_path_xml) as stream_file:
        stream = stream_file.read()

    os.remove(file_path_pdf)
    os.remove(file_path_xml)
    os.remove(file_xml_metadata_path)
    shutil.rmtree(file_xml_data_path)

    return stream
