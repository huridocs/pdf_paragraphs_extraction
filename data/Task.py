import datetime

from pydantic import BaseModel


class Task(BaseModel):
    tenant: str
    pdf_file_name: str
    datetime: datetime.datetime
