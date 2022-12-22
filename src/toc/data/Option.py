from pydantic import BaseModel


class Option(BaseModel):
    id: str
    label: str
