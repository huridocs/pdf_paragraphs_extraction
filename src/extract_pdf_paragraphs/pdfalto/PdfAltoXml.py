import os
import platform
import shutil
import pathlib
import subprocess
import uuid

from bs4 import BeautifulSoup


THIS_SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()


def create_xml_from_pdf(pdf_path, file_path_xml):
    if platform.system() == "Darwin":
        pdfalto_executable = f"{THIS_SCRIPT_PATH}/pdfalto_macos"
    else:
        pdfalto_executable = f"{THIS_SCRIPT_PATH}/pdfalto_linux"

    subprocess.run([pdfalto_executable, "-readingOrder", pdf_path, file_path_xml])


def get_file_path(file_name, extension):
    if not os.path.exists(f"{THIS_SCRIPT_PATH}/../../../docker_volume/files_pdfalto"):
        os.makedirs(f"{THIS_SCRIPT_PATH}/../../../docker_volume/files_pdfalto")

    if not os.path.exists(
        f"{THIS_SCRIPT_PATH}/../../../docker_volume/files_pdfalto/{extension}"
    ):
        os.makedirs(
            f"{THIS_SCRIPT_PATH}/../../../docker_volume/files_pdfalto/{extension}"
        )

    return f"{THIS_SCRIPT_PATH}/../../../docker_volume/files_pdfalto/{extension}/{file_name}.{extension}"


def get_xml_tags_from_file_content(file_content):
    file_id = str(uuid.uuid1())

    file_path_pdf = pathlib.Path(get_file_path(file_id, "pdf"))
    file_path_pdf.write_bytes(file_content)

    file_path_xml = get_file_path(file_id, "xml")
    file_xml_metadata_path = file_path_xml.replace(".xml", "_metadata.xml")
    file_xml_data_path = file_path_xml.replace(".xml", ".xml_data")

    create_xml_from_pdf(file_path_pdf, file_path_xml)

    with open(file_path_xml) as stream:
        xml_tags = BeautifulSoup(stream.read(), "lxml-xml")

    os.remove(file_path_pdf)
    os.remove(file_path_xml)
    os.remove(file_xml_metadata_path)
    shutil.rmtree(file_xml_data_path)

    return xml_tags
