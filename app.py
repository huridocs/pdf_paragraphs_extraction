import json
import os

import pymongo
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import PlainTextResponse
import sys

from ServiceConfig import ServiceConfig
from data.SegmentBox import SegmentBox
from extract_pdf_paragraphs.PdfFeatures.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.pdfalto.PdfAltoXml import get_xml_tags_from_file_content
from extract_pdf_paragraphs.segmentator.predict import predict
from data.ExtractionData import ExtractionData
from pdf_file.PdfFile import PdfFile

config = ServiceConfig()
logger = config.get_logger('service')

app = FastAPI()

logger.info(f'Get PDF paragraphs service has started')


@app.get('/info')
async def info():
    logger.info('Get PDF paragraphs info endpoint')
    return sys.version


@app.get('/error')
async def error():
    logger.error("This is a test error from the error endpoint")
    raise HTTPException(status_code=500, detail='This is a test error from the error endpoint')


@app.post('/async_extraction/{tenant}')
async def async_extraction(tenant, file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        pdf_file = PdfFile(tenant)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        return 'task registered'
    except Exception:
        logger.error(f'Error adding task {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error adding task {filename}')


@app.get('/')
async def extract_paragraphs(file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        xml_tags = get_xml_tags_from_file_content(file.file.read())
        pdf_features = PdfFeatures.from_xml_content(xml_tags)
        pdf_segments = predict(pdf_features)
        paragraphs = [SegmentBox.from_pdf_segment(x).dict() for x in pdf_segments]
        return json.dumps({'page_width': pdf_features.pages[0].page_width,
                           'page_height': pdf_features.pages[0].page_height,
                           'paragraphs': paragraphs})
    except Exception:
        logger.error(f'Error segmenting {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error segmenting {filename}')


@app.get('/get_paragraphs/{tenant}/{pdf_file_name}')
async def get_paragraphs(tenant: str, pdf_file_name: str):
    try:
        client = pymongo.MongoClient('mongodb://mongo_paragraphs:27017')

        suggestions_filter = {"tenant": tenant, "file_name": pdf_file_name}

        pdf_paragraph_db = client['pdf_paragraph']
        extraction_data_dict = pdf_paragraph_db.paragraphs.find_one(suggestions_filter)
        pdf_paragraph_db.paragraphs.delete_many(suggestions_filter)

        extraction_data = ExtractionData(**extraction_data_dict)
        return extraction_data.json()
    except TypeError:
        raise HTTPException(status_code=404, detail='No paragraphs')
    except Exception:
        logger.error('Error', exc_info=1)
        raise HTTPException(status_code=422, detail='An error has occurred. Check graylog for more info')


@app.get('/get_xml/{tenant}/{pdf_file_name}', response_class=PlainTextResponse)
async def get_xml(tenant: str, pdf_file_name: str):
    try:
        xml_file_name = '.'.join(pdf_file_name.split('.')[:-1]) + '.xml'

        with open(f'./docker_volume/xml/{tenant}/{xml_file_name}', mode='r') as file:
            content = file.read()
            os.remove(f'./docker_volume/xml/{tenant}/{xml_file_name}')
            return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='No xml file')
    except Exception:
        logger.error('Error', exc_info=1)
        raise HTTPException(status_code=422, detail='An error has occurred. Check graylog for more info')


