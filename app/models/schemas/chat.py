from pydantic import BaseModel , ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
from typing import Literal, Union, Dict, Any
from uuid import UUID




class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    content: str

class SessionInfo(BaseModel):
    id: UUID
    title: str
    is_new: bool


class UserMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # role: Literal["user"]
    content: str
    created_at: datetime


class AssistantMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # role: Literal["assistant"]
    agent_metadata: Dict[str, Any]
    created_at: datetime


class ChatResponse(BaseModel):
    session: SessionInfo
    user_message: UserMessageRead
    agent_message: AssistantMessageRead

class SessionTitleUpdate(BaseModel):
    title: str