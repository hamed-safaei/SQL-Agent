from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class MessageBase(BaseModel):

    session_id: int

    role: str

    content: Optional[str] = None

    agent_metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):

    user_id: int

    content: str


class Message(MessageBase):

    id: int

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageRead(MessageBase):

    id: int

    created_at: datetime