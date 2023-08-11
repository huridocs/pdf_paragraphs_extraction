import json
import logging
import os
from contextlib import asynccontextmanager

import pymongo
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import PlainTextResponse
import sys

from lxml import etree
from lxml.etree import ElementBase
from pdf_features.PdfFeatures import PdfFeatures
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import sentry_sdk

from extract_pdf_paragraphs.pdf_to_xml import pdf_content_to_pdf_path
from extract_pdf_paragraphs.segmentator.predict import predict
from data.ExtractionData import ExtractionData
from pdf_file.PdfFile import PdfFile
import config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = pymongo.MongoClient(f"{config.MONGO_HOST}:{config.MONGO_PORT}")
    yield
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

logger.info("Get PDF paragraphs service has started")

try:
    sentry_sdk.init(
        os.environ.get("SENTRY_DSN"),
        traces_sample_rate=0.1,
        environment=os.environ.get("ENVIRONMENT", "development"),
    )
    app.add_middleware(SentryAsgiMiddleware)
except Exception:
    pass


@app.get("/info")
async def info():
    logger.info("Get PDF paragraphs info endpoint")
    return sys.version


@app.get("/error")
async def error():
    logger.error("This is a test error from the error endpoint")
    raise HTTPException(status_code=500, detail="This is a test error from the error endpoint")


@app.post("/async_extraction/{tenant}")
async def async_extraction(tenant, file: UploadFile = File(...)):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        pdf_file = PdfFile(tenant)
        pdf_file.save(pdf_file_name=filename, file=file.file.read())
        return "task registered"
    except Exception:
        logger.error(f"Error adding task {filename}", exc_info=1)
        raise HTTPException(status_code=422, detail=f"Error adding task {filename}")


@app.post("/")
async def extract_paragraphs(file: UploadFile):
    filename = '"No file name! Probably an error about the file in the request"'
    try:
        filename = file.filename
        pdf_path = pdf_content_to_pdf_path(file.file.read())
        pdf_features = PdfFeatures.from_pdf_path(pdf_path)
        pdf_segments = predict(pdf_features)
        paragraphs = [x.to_segment_box().dict() for x in pdf_segments]
        return json.dumps(
            {
                "page_width": pdf_features.pages[0].page_width,
                "page_height": pdf_features.pages[0].page_height,
                "paragraphs": paragraphs,
            }
        )
    except Exception:
        logger.error(f"Error segmenting {filename}", exc_info=1)
        raise HTTPException(status_code=422, detail=f"Error segmenting {filename}")


@app.post("/pdf_to_xml", response_class=PlainTextResponse)
async def pdf_to_xml(file: UploadFile = File(...)):
    try:
        pdf_path = pdf_content_to_pdf_path(file.file.read())
        file: str = open(pdf_path).read()
        file_bytes: bytes = file.encode("utf-8")
        root: ElementBase = etree.fromstring(file_bytes)
        return root
    except Exception:
        logger.error("Error extracting xml", exc_info=1)
        raise HTTPException(status_code=422, detail="Error extracting xml")


@app.get("/get_paragraphs/{tenant}/{pdf_file_name}")
async def get_paragraphs(tenant: str, pdf_file_name: str):
    try:
        suggestions_filter = {"tenant": tenant, "file_name": pdf_file_name}
        pdf_paragraph_db = app.mongodb_client["pdf_paragraph"]
        extraction_data_dict = pdf_paragraph_db.paragraphs.find_one(suggestions_filter)
        pdf_paragraph_db.paragraphs.delete_many(suggestions_filter)

        extraction_data = ExtractionData(**extraction_data_dict)
        return extraction_data.json()
    except TypeError:
        raise HTTPException(status_code=404, detail="No paragraphs")
    except Exception:
        logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="An error has occurred. Check graylog for more info")


@app.get("/get_xml/{tenant}/{pdf_file_name}", response_class=PlainTextResponse)
async def get_xml(tenant: str, pdf_file_name: str):
    try:
        xml_file_name = pdf_file_name.replace(".", "") + ".xml"

        with open(
            f"{config.DATA_PATH}/xml/{tenant}/{xml_file_name}",
            mode="r",
        ) as file:
            content = file.read()
            os.remove(f"{config.DATA_PATH}/xml/{tenant}/{xml_file_name}")
            return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No xml file")
    except Exception:
        logger.error("Error", exc_info=1)
        raise HTTPException(status_code=422, detail="An error has occurred. Check graylog for more info")
