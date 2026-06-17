from pydantic import BaseModel , ConfigDict , Field
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any
from app.models.schemas import SessionInfo
from uuid import UUID



class ChatRequest(BaseModel):
    session_id: Optional[UUID] = Field(default=None, examples=[None])
    content:    str
    streaming:  bool = Field(default=False, description="True → SSE stream, False → JSON")
 

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
    agent_msg_id: int = Field(validation_alias="id")

class ChatResponse(BaseModel):
    session: SessionInfo
    # user_message: UserChat
    assistant: AssistantChat
    message : Message
    





