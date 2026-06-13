from pydantic import BaseModel , ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any
from app.models.schemas import SessionInfo
from uuid import UUID



class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    content: str


class UserChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str
    created_at: datetime


class AssistantChat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    agent_metadata: Dict[str, Any]
    # created_at: datetime


class ChatResponse(BaseModel):
    session: SessionInfo
    # user_message: UserChat
    assistant: AssistantChat



