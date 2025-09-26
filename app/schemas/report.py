from pydantic import BaseModel
from typing import Dict, Any


class ReportRunRequest(BaseModel):
    report_name: str
    parameters: Dict[str, Any] = {}


