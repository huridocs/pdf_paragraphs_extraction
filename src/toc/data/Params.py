from typing import Optional

from pydantic import BaseModel

from data.Option import Option


class Params(BaseModel):
    property_name: str
    options: Optional[list[Option]] = None
    multi_value: bool = False
