from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any


class getUserMessage(BaseModel):
    role: Literal["user"]
    content: str
    created_at: datetime


class getAssistantMessage(BaseModel):
    role: Literal["assistant"]
    agent_metadata: Dict[str, Any]
    created_at: datetime


MessageRead = Union[
    getUserMessage,
    getAssistantMessage
]