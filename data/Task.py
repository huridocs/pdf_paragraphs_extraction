from pydantic import BaseModel


class Task(BaseModel):
    tenant: str
    task: str
