from pydantic import BaseModel
from data.Params import Params


class MetadataExtractionTask(BaseModel):
    tenant: str
    task: str
    params: Params
