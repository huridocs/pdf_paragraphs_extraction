from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class Paragraphs(BaseModel):
    page_width: int
    page_height: int
    paragraphs: list[SegmentBox]
