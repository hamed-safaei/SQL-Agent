# from typing import Optional, Any
# from typing_extensions import TypedDict


# class AgentState(TypedDict):

#     question: str

#     mode: Optional[str]

#     message: Optional[str]

#     intro_message: Optional[str]

#     sql_message: Optional[str]

#     sql: Optional[str]

#     result: Optional[Any]

#     analysis: Optional[str]

#     error: Optional[str]








from typing import Optional, Any
from typing_extensions import TypedDict


class AgentState(TypedDict):
    question:      str
    mode:          Optional[str]
    message:       Optional[str]   # chat node final message
    sql:           Optional[str]   # generated SQL
    result:        Optional[Any]   # query execution result
    intro_message: Optional[str]   # full mode intro
    sql_message:   Optional[str]   # full mode sql explanation
    analysis:      Optional[str]   # full mode analysis