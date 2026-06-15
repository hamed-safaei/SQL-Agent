from pydantic import BaseModel , ConfigDict , Field
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any
from app.models.schemas import SessionInfo
from uuid import UUID



class ChatRequest(BaseModel):
    session_id: Optional[UUID] = Field(default=None, examples=[None])
    content: str


class UserChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str
    created_at: datetime


class AssistantChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mode: str
    agent_metadata: Dict[str, Any]


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : int


class ChatResponse(BaseModel):
    session: SessionInfo
    # user_message: UserChat
    assistant: AssistantChat
    message : Message
    



