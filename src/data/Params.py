from pydantic import BaseModel


class Params(BaseModel):
    filename: str
