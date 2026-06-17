# from pydantic import BaseModel, ConfigDict
# from typing import Optional, Any, Dict
# from datetime import datetime
# from typing import Literal, Union, Dict, Any


# class getUserMessage(BaseModel):
#     role: Literal["user"]
#     content: str
#     created_at: datetime


# class getAssistantMessage(BaseModel):
#     role: Literal["assistant"]
#     agent_metadata: Dict[str, Any]
#     created_at: datetime


# MessageRead = Union[
#     getUserMessage,
#     getAssistantMessage
# ]


from pydantic import BaseModel
from typing import Literal, Dict, Any
from datetime import datetime


class getUserMessage(BaseModel):
    role: Literal["user"]
    message: str
    created_at: datetime


class getAssistantMessage(BaseModel):
    role: Literal["assistant"]
    mode: str
    agent_metadata: Dict[str, Any]
    created_at: datetime


MessageRead = getUserMessage | getAssistantMessage