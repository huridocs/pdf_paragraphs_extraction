from pydantic import BaseModel

from data.Params import Params


class ExtractionMessage(BaseModel):
    tenant: str
    task: str
    params: Params
    success: bool
    error_message: str = None
    data_url: str = None
    file_url: str = None
