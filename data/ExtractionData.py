from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class ExtractionData(BaseModel):
    tenant: str
    pdf_file_name: str
    paragraphs: List[SegmentBox]
