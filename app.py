from fastapi import FastAPI, HTTPException, File, UploadFile
import sys
from get_graylog import get_graylog
from information_extraction.InformationExtraction import InformationExtraction

from segments_boxes.SegmentsBoxes import SegmentsBoxes
from tasks.Tasks import Tasks

graylog = get_graylog()

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
        tasks = Tasks()
        tasks.add(filename=filename, file=file.file.read())
        return 'task registered'
    except Exception:
        graylog.error(f'Error adding task {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error adding task {filename}')


@app.post('/add_segmentation_task/{tenant}')
async def add_segmentation_task_with_tenant(tenant, file: UploadFile  = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        tasks = Tasks(tenant)
        tasks.add(filename=filename, file=file.file.read())
        return 'task registered'
    except Exception:
        graylog.error(f'Error adding task {filename}', exc_info=1)
        raise HTTPException(status_code=422, detail=f'Error adding task {filename}')
