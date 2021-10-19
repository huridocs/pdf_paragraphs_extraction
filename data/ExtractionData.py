from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class ExtractionData(BaseModel):
    tenant: str
    file_name: str
    paragraphs: List[SegmentBox]
