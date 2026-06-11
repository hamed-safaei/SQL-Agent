from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any


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


# class MessageRead(MessageBase):
#     id: int
#     created_at: datetime


class UserMessageRead(BaseModel):
    role: Literal["user"]
    content: str
    created_at: datetime


class AssistantMessageRead(BaseModel):
    role: Literal["assistant"]
    agent_metadata: Dict[str, Any]
    created_at: datetime


MessageRead = Union[
    UserMessageRead,
    AssistantMessageRead
]