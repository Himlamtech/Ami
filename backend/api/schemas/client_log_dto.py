from pydantic import BaseModel
from typing import Optional


class ClientLogRequest(BaseModel):
    level: str
    message: str
    stack: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[dict] = None
