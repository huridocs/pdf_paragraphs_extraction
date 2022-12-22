from pydantic import BaseModel
from data.Params import Params


class ResultsMessage(BaseModel):
    tenant: str
    task: str
    params: Params
    success: bool
    error_message: str
    data_url: str = None
