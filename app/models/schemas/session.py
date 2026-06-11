# from pydantic import BaseModel, ConfigDict
# from datetime import datetime
# from app.models.schemas.message import Message


# class SessionBase(BaseModel):
#     user_id: int




# class SessionsRead(SessionBase):
#     id: int
#     created_at: datetime
#     messages: list[Message] = []
#     model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.schemas.message import Message
from uuid import UUID


class SessionBase(BaseModel):
    user_id: int


class SessionCreate(BaseModel):
    """برای ساخت session جدید - فقط user_id کافی است"""
    user_id: int


class SessionSummary(BaseModel):
    """برای لیست session های کاربر - فقط id و title"""
    id: UUID
    title: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SessionsRead(SessionBase):
    id: int
    created_at: datetime
    messages: list[Message] = []
    model_config = ConfigDict(from_attributes=True)