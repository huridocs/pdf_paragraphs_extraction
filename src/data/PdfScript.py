from pydantic import BaseModel
from pydantic.main import Enum


class ScriptsType(Enum):
    SUPER_SCRIPT = "SUPER-SCRIPT"
    SUB_SCRIPT = "SUB-SCRIPT"
    REGULAR_TEXT = "REGULAR-TEXT"


class PdfScript(BaseModel):
    start_character: int = 0
    end_character: int = 0
    type: ScriptsType

    class Config:
        use_enum_values = True
