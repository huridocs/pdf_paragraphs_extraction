from pydantic import BaseModel


class ExtractionMessage(BaseModel):
    tenant: str
    pdf_file_name: str
    success: bool
    error_message: str = None
    results_url: str = None
    file_results_url: str = None

