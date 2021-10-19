from pydantic import BaseModel

from data.Params import Params


class Task(BaseModel):
    tenant: str
    task: str
    params: Params
