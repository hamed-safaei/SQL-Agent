from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .schemas.agent import IntentOutput


BASE_URL = "https://api.gapgpt.app/v1"
API_KEY  = "sk-s8KnoW59PPxeHBvyzENeVoEiH2QbiNm1PxJt20H586up5p8n"
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


intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an intent classifier for a SQL agent.
Classify the user request into one of these modes:
chat   → greeting or unrelated to database
sql    → user explicitly asks for SQL query only
result → user wants only the raw result (no explanation)
full   → default for any data question (intro + sql + explanation + analysis)
"""),
    ("human", "{question}"),
])
intent_chain = intent_prompt | llm.with_structured_output(IntentOutput)


chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a SQL intelligent assistant.
You MUST always respond in Persian (Farsi) language only.
Only answer SQL and database-related questions.
"""),
    ("human", "{question}"),
])
chat_chain = chat_prompt | streaming_llm



sql_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a SQL expert in PostgreSQL.
Generate a PL/pgSQL query based on the schema.
Do not explain anything.
Only produce raw SQL – no markdown, no code fences.

Schema:
{schema}
"""),
    ("human", "{question}"),
])
sql_chain = sql_prompt | streaming_llm



intro_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful data analyst assistant. You MUST respond only in Persian (Farsi).
Write a short Persian introductory sentence (1-2 sentences max) that tells the user
you are about to show them a SQL query for their request.
Be natural and vary the phrasing. Do not produce any SQL or markdown.
"""),
    ("human", "{question}"),
])
intro_chain = intro_prompt | streaming_llm




sql_message_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful data analyst assistant. You MUST respond only in Persian (Farsi).
Write a short Persian explanation (2-3 sentences) of what the provided SQL query does,
and end with a natural sentence indicating the result will follow.
Do not produce any SQL or markdown.
"""),
    ("human", "Question: {question}\n\nSQL: {sql}"),
])
sql_message_chain = sql_message_prompt | streaming_llm




analyzer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a helpful data analyst.
You MUST always respond in Persian (Farsi) language only. Never respond in English.
Analyze the provided query result and write a concise, insightful Persian summary.
Always give answers with new lines and in separate paragraphs or organized lists.

Do not produce any Markdown.
Do not use any symbols like **, ###, ```, *, -, 1.
Produce only plain text.
Always give the answer in several separate paragraphs or as a list,
each item on a separate line, without any Markdown characters.
Separate lines by going to the next line.
"""),
    ("human", "Question: {question}\n\nSQL: {sql}\n\nResult: {result}"),
])
analyzer_chain = analyzer_prompt | streaming_llm