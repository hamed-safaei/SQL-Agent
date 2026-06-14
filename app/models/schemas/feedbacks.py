from typing import Literal

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    message_id: int
    rating: Literal[1, -1]
    reason_code: str | None = Field(default=None, max_length=50)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    rating: int
    reason_code: str | None
    comment: str | None

    class Config:
        from_attributes = True