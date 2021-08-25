import json

import pymongo
from fastapi import FastAPI, HTTPException, File, UploadFile
import sys

from data.ExtractionData import ExtractionData
from data.SegmentBox import SegmentBox
from get_graylog import get_graylog
from information_extraction.InformationExtraction import InformationExtraction

from tasks.Tasks import Tasks

graylog = get_graylog()

app = FastAPI()

graylog.info(f'Get PDF paragraphs service has started')


def sanitize_name(name: str):
    return ''.join(x if x.isalnum() else '_' for x in name)


@app.get('/info')
async def info():
    graylog.info('Get PDF paragraphs info endpoint')
    return sys.version


@app.get('/error')
async def error():
    graylog.error("This is a test error from the error endpoint")
    raise HTTPException(status_code=500, detail='This is a test error from the error endpoint')


@app.get('/')
async def get_paragraphs(file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        information_extraction = InformationExtraction.from_file_content(file.file.read())
        paragraphs = [SegmentBox.from_segment(x).dict() for x in information_extraction.segments]
        return json.dumps({'page_width': information_extraction.pdf_features.page_width,
                           'page_height': information_extraction.pdf_features.page_height,
                           'paragraphs': paragraphs})
    except Exception:
        graylog.error(f'Error segmenting {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error segmenting {filename}')


@app.post('/async_extraction/{tenant}')
async def add_async_extraction(tenant, file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    tenant = sanitize_name(tenant)
    try:
        filename = file.filename
        tasks = Tasks(tenant)
        tasks.add(filename=filename, file=file.file.read())
        return 'task registered'
    except Exception:
        graylog.error(f'Error adding task {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error adding task {filename}')


@app.get('/get_paragraphs/{tenant}/{xml_file_name}')
async def get_paragraphs(tenant: str, xml_file_name: str):
    tenant = sanitize_name(tenant)
    xml_file_name = sanitize_name(xml_file_name)
    try:
        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')
        pdf_paragraph_db = client['pdf_paragraph']
        suggestions_filter = {"tenant": tenant, "xml_file_name": xml_file_name}

        extraction_data_dict = pdf_paragraph_db.paragraphs.find_one(suggestions_filter)

        extraction_data = ExtractionData(**extraction_data_dict)
        pdf_paragraph_db.paragraphs.delete_many(suggestions_filter)
        return extraction_data.json()
    except TypeError:
        raise HTTPException(status_code=404, detail='No paragraphs')
    except Exception:
        graylog.error('Error', exc_info=1)
        raise HTTPException(status_code=422, detail='An error has occurred. Check graylog for more info')
