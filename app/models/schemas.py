from pydantic import BaseModel , ConfigDict
from typing import Literal, Optional, Any , Dict
from typing_extensions import TypedDict
from datetime import datetime

#LLM Output Models

class IntentOutput(BaseModel):
    mode: Literal["chat", "sql", "result", "full"]


class ChatOutput(BaseModel):
    message: str


class SQLOutput(BaseModel):
    sql: str


class FullOutput(BaseModel):
    intro_message: str
    sql: str
    sql_message: str


class AnalysisOutput(BaseModel):
    analysis: str


#Graph State

class AgentState(TypedDict):
    question: str
    mode: Optional[str]
    message: Optional[str]
    intro_message: Optional[str]
    sql_message: Optional[str]
    sql: Optional[str]
    result: Optional[Any]
    analysis: Optional[str]
    error: Optional[str]



    # /////




# --- Message Schemas ---
class MessageBase(BaseModel):
    session_id: int
    role: str  # 'user' یا 'assistant'
    content: Optional[str] = None
    agent_metadata: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    user_id: int
    content: str


class Message(MessageBase):
    id: int
    created_at: datetime
    
    # این مدل کانفیگ باعث میشه Pydantic با SQLAlchemy کار کنه
    model_config = ConfigDict(from_attributes=True)

class MessageRead(MessageBase):
    id: int
    created_at: datetime
    # می‌توانید session_id را حذف کنید یا نگه دارید

# --- Session Schemas ---
class SessionBase(BaseModel):
    user_id: int
    is_active: bool = True

class SessionCreate(BaseModel):
    user_id: int

class Session(SessionBase):
    id: int
    created_at: datetime
    messages: list[Message] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

# فقط اطلاعات کاربر بدون سشن‌ها
class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# اطلاعات کاربر همراه با سشن‌ها (برای صفحاتی که نیاز داری)
class UserWithSessions(UserRead):
    sessions: list[Session] = []






class QueryRequest(BaseModel):
    question: str

class ConnectionTest(BaseModel):
    server: str
    database: str