from dataclasses import dataclass
from typing import Any
from session import Session
from pydantic import BaseModel

@dataclass
class InternalEvent:
    name: str
    body: Any


class ExceptionEvent(BaseModel):
    error: Exception
    event: InternalEvent
    session: Session

    class Config:
        arbitrary_types_allowed = True
