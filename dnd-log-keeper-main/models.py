
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LogEntry(BaseModel):
    session_id: str
    timestamp: Optional[str] = datetime.utcnow().isoformat()
    speaker: Optional[str] = "Narrator"
    content: str
    tags: Optional[List[str]] = []

class SessionRequest(BaseModel):
    session_id: str
