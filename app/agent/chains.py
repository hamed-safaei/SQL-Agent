from langchain_openai import ChatOpenAI

from .schemas.agent import IntentOutput
from .prompts import (
    intent_prompt,
    chat_prompt,
    sql_prompt,
    intro_prompt,
    sql_message_prompt,
    analyzer_prompt,
)


from app.core.config import settings



BASE_URL = "https://api.gapgpt.app/v1"
API_KEY  = settings.OPENAI_API_KEY
MODEL    = "gpt-4o"


llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    temperature=0,
    streaming=False,
)

streaming_llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    temperature=0,
    streaming=True,
)


intent_chain      = intent_prompt      | llm.with_structured_output(IntentOutput)
chat_chain        = chat_prompt        | streaming_llm
sql_chain         = sql_prompt         | streaming_llm
intro_chain       = intro_prompt       | streaming_llm
sql_message_chain = sql_message_prompt | streaming_llm
analyzer_chain    = analyzer_prompt    | streaming_llm