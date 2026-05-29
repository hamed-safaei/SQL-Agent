from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.schemas.message import Message


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