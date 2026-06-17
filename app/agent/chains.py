# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from app.core.config import settings
# from app.agent.schemas  import (
#     IntentOutput,
#     ChatOutput,
#     SQLOutput,
#     FullOutput,
#     AnalysisOutput,
# )


# #LLM Setup 

# llm = ChatOpenAI(
#     base_url="https://api.gapgpt.app/v1",
#     api_key=settings.OPENAI_API_KEY,
#     model="gpt-4o",
#     temperature=0,
#     streaming=False
# )

# streaming_llm = ChatOpenAI(
#     base_url="https://api.gapgpt.app/v1",
#     api_key=settings.OPENAI_API_KEY,
#     model="gpt-4o",
#     temperature=0,
#     streaming=True
# )


# #Prompts 

# intent_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# You are an intent classifier for a SQL agent.

# Classify the user request into one of these modes:

# chat   → greeting or unrelated to database
# sql    → user explicitly asks for SQL query only
# result → user wants only the raw result
# full   → default for any data question

# Important:
# If the user asks about data, ranking, statistics, counts, etc.,
# and does NOT explicitly request SQL only,
# you MUST return full.
# """),
#     ("human", "{question}")
# ])

# chat_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# You are a SQL intelligent assistant connected to the user's database.
# You MUST always respond in Persian (Farsi) language only. Never respond in English or any other language.

# Mirror the user's tone and formality:
# - If they're casual and warm, be friendly and conversational.
# - If they're direct and brief, keep it short and to the point.
# - If they greet you, greet back warmly, then briefly mention what you do.
# - If they don't greet you, never greet them.
# - If they jump straight to questions, skip the pleasantries and get to work.

# Your role:
# You help users query their SQL database through natural language. Users can ask questions and receive:
# - SQL queries
# - Query results in table format
# - Analysis and insights

# Stay focused:
# Only answer SQL and database-related questions.
# If asked something irrelevant, politely redirect in Persian: "من فقط می‌توانم در مورد سوالات دیتابیس و SQL کمک کنم."

# """),
#     ("human", "{question}")
# ])

# sql_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# You are a SQL expert in Postgresql .

# Generate a pl-sql query based on the schema.
# Do not explain anything.
# Only produce SQL.

# Schema:
# {schema}
# """),
#     ("human", "{question}")
# ])

# full_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# You are a data analyst assistant. You MUST respond only in Persian (Farsi).

# For the user question, generate exactly these three fields:

# 1. intro_message
# - Write a Persian introductory message.
# - It should explain that you prepared a SQL query for the user's request.
# - It must end in a natural way that indicates the SQL query will be shown immediately next.
# - Example style:
#   "کوئری مربوط به این درخواست به شرح زیر است."
#   or
#   "در ادامه می‌توانید کوئری تولیدشده را مشاهده کنید."
#   Don't always use the same sentence, be creative.

# 2. sql
# - Generate a valid pl-sql query.

# 3. sql_message
# - Write a Persian explanation of what the SQL query does.
# - It must end in a natural way that indicates the query result will be shown immediately next.
# - Example style:
#   "نتیجه این کوئری در ادامه آمده است."
#   or
#   "در ادامه می‌توانید خروجی این کوئری را مشاهده کنید."
#   Don't always use the same sentence, be creative.

# Rules:
# - Both messages MUST be in Persian (Farsi). This is mandatory.
# - Keep both messages clear and natural.
# - Do not include markdown code fences.
# - Do not include SQL inside the messages.

# Database schema:
# {schema}
# """),
#     ("human", "{question}")
# ])

# analyzer_prompt = ChatPromptTemplate.from_messages([
#     ("system", """
# You are a helpful data analyst.
# You MUST always respond in Persian (Farsi) language only. Never respond in English.
# Analyze the provided query result and write a concise, insightful Persian summary.
# Always give answers with new lines and in separate paragraphs or organized lists.
     

# Do not produce any Markdown.
# Do not use any symbols like **, ###,
# ```, *, -, 1.
# Produce only plain text.
# Always give the answer in several separate paragraphs or as a list, each item on a separate line, but without any Markdown characters.
# Separate lines by going to the next line     
# """),
#     ("human", "Question: {question}\n\nSQL: {sql}\n\nResult: {result}")
# ])


# #Chains

# intent_chain = intent_prompt | llm.with_structured_output(IntentOutput)
# chat_chain = chat_prompt | llm.with_structured_output(ChatOutput)
# sql_chain = sql_prompt | llm.with_structured_output(SQLOutput)
# full_chain = full_prompt | llm.with_structured_output(FullOutput)
# analyzer_chain = analyzer_prompt | llm.with_structured_output(AnalysisOutput)






from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .schemas.agent import IntentOutput

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
BASE_URL = "https://api.gapgpt.app/v1"
API_KEY  = "sk-s8KnoW59PPxeHBvyzENeVoEiH2QbiNm1PxJt20H586up5p8n"
MODEL    = "gpt-4o"

# ─────────────────────────────────────────
# LLM instances
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Intent
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Chat
# ─────────────────────────────────────────
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a SQL intelligent assistant.
You MUST always respond in Persian (Farsi) language only.
Only answer SQL and database-related questions.
"""),
    ("human", "{question}"),
])
chat_chain = chat_prompt | streaming_llm

# ─────────────────────────────────────────
# SQL generation  (sql / result / full modes)
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Full mode – intro
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Full mode – SQL explanation
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# Full mode – result analysis
# ─────────────────────────────────────────
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