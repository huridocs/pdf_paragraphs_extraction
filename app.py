import os
import pathlib

from fastapi import FastAPI, HTTPException, File, UploadFile
import sys
import logging
import graypy

from information_extraction.InformationExtraction import InformationExtraction
from information_extraction.SegmentsBoxes import SegmentsBoxes
import yaml

graylog = logging.getLogger('graylog')
graylog.setLevel(logging.INFO)

if os.path.exists('graylog.yml'):
    graylog_ip = yaml.safe_load(open("graylog.yml", 'r'))['graylog_ip']
    handler = graypy.GELFUDPHandler(graylog_ip, 12201, localname="get_pdf_paragraphs")
    graylog.addHandler(handler)

app = FastAPI()

graylog.info(f'Get PDF paragraphs service has started')


@app.get('/info')
def info():
    graylog.info('Get PDF paragraphs info endpoint')
    return sys.version


@app.get('/error')
def error():
    graylog.error("This is a test error from the error endpoint")
    raise HTTPException(status_code=500, detail='This is a test error from the error endpoint')


@app.post('/')
def segment(file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        information_extraction = InformationExtraction.from_file_content(file.file.read(), True)
        segmented_boxes = SegmentsBoxes.from_information_extraction(information_extraction)
        return segmented_boxes.to_json()
    except Exception:
        graylog.error(f'Error segmenting {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error segmenting {filename}')


@app.post('/add_segmentation_task')
def add_segmentation_task(file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        if not os.path.exists('./docker_volume/to_segment'):
            os.mkdir('./docker_volume/to_segment')

        file_path_pdf = pathlib.Path(f'./docker_volume/to_segment/{filename}')
        content = file.file.read()
        file_path_pdf.write_bytes(content)
        return 'task registered'
    except Exception:
        graylog.error(f'Error segmenting {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error segmenting {filename}')


@app.post('/execute_segmentation_task')
def execute_segmentation_task():
    try:
        raise HTTPException(status_code=500, detail='This is a test error from the execute_segmentation_task endpoint')
    except Exception:
        graylog.error('Error in segmentation task', exc_info=1)
        raise HTTPException(status_code=422, detail='Error in segmentation task')
