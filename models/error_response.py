from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    err : str
    status_code: int
    message: Optional[str] = None