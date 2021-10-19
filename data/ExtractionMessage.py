from pydantic import BaseModel


class ExtractionMessage(BaseModel):
    tenant: str
    task: str
    success: bool
    error_message: str = None
    data_url: str = None
    file_url: str = None

