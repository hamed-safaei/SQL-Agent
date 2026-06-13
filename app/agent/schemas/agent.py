from pydantic import BaseModel
from typing import Literal


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