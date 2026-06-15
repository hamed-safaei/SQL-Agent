import asyncio
from typing import Optional, Any
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter
import asyncio
from typing import Optional, Any
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
BASE_URL = "https://api.gapgpt.app/v1"
API_KEY  = "sk-s8KnoW59PPxeHBvyzENeVoEiH2QbiNm1PxJt20H586up5p8n"
MODEL    = "gpt-4o"

# ─────────────────────────────────────────
# LLMs
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
# Schemas
# ─────────────────────────────────────────
class IntentOutput(BaseModel):
    mode: str = Field(description="chat | sql | result | full")

# ─────────────────────────────────────────
# State
# ─────────────────────────────────────────
class AgentState(TypedDict):
    question:      str
    mode:          Optional[str]
    message:       Optional[str]   # chat node final message
    sql:           Optional[str]   # generated SQL
    result:        Optional[Any]   # query execution result
    intro_message: Optional[str]   # full mode intro
    sql_message:   Optional[str]   # full mode sql explanation
    analysis:      Optional[str]   # full mode analysis

# ─────────────────────────────────────────
# Helpers  (stubs – replace with your real implementations)
# ─────────────────────────────────────────
def get_db_schema_text() -> str:
    """Return the database schema as plain text."""
    # TODO: replace with your real schema loader
    return """
    TABLE users (id SERIAL PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP);
    TABLE orders (id SERIAL PRIMARY KEY, user_id INT REFERENCES users(id), total NUMERIC, created_at TIMESTAMP);
    TABLE products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC, stock INT);
    TABLE order_items (id SERIAL PRIMARY KEY, order_id INT REFERENCES orders(id), product_id INT REFERENCES products(id), quantity INT);
    """

def run_sql_query(sql: str) -> Any:
    """Execute the SQL and return the result."""
    # TODO: replace with your real DB executor
    return [{"id": 1, "name": "Alice", "total": 250.0}]

# ─────────────────────────────────────────
# Prompts & Chains
# ─────────────────────────────────────────

# --- Intent ---
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

# --- Chat ---
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a SQL intelligent assistant.
You MUST always respond in Persian (Farsi) language only.
Only answer SQL and database-related questions.
"""),
    ("human", "{question}"),
])
chat_chain = chat_prompt | streaming_llm

# --- SQL generation (used in sql, result, full modes) ---
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

# --- Full mode: intro message ---
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

# --- Full mode: sql explanation message ---
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

# --- Full mode: result analysis ---
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

# ─────────────────────────────────────────
# Nodes
# ─────────────────────────────────────────

# ── Intent (no streaming needed) ──────────────────────────────────────────────
def intent_node(state: AgentState):
    result = intent_chain.invoke({"question": state["question"]})
    return {"mode": result.mode}

# ── Router ────────────────────────────────────────────────────────────────────
def router(state: AgentState):
    return state["mode"]

# ── Chat (streaming) ──────────────────────────────────────────────────────────
def chat_node(state: AgentState, writer: StreamWriter):
    full_message = ""
    for chunk in chat_chain.stream({"question": state["question"]}):
        token = chunk.content
        if token:
            full_message += token
            writer({"type": "token", "node": "chat", "value": token})
    return {"message": full_message}

# ── SQL only (streaming) ──────────────────────────────────────────────────────
def sql_node(state: AgentState, writer: StreamWriter):
    """Mode = sql  →  stream the generated query, nothing else."""
    schema_text = get_db_schema_text()
    full_sql = ""
    for chunk in sql_chain.stream({"question": state["question"], "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "sql", "value": token})
    return {"sql": full_sql}

# ── Result  (sql streaming → execute without streaming) ───────────────────────
def result_node(state: AgentState, writer: StreamWriter):
    """
    Mode = result
    1. Stream the SQL generation tokens so the user can watch it appear.
    2. Wait until the full SQL is ready, then execute and return the result at once.
    """
    schema_text = get_db_schema_text()

    # Step 1 – stream SQL tokens
    full_sql = ""
    for chunk in sql_chain.stream({"question": state["question"], "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "sql", "value": token})

    # Step 2 – execute (blocking, no streaming)
    query_result = run_sql_query(full_sql)
    writer({"type": "result", "node": "result", "value": query_result})

    return {"sql": full_sql, "result": query_result}

# ── Full  (multi-step streaming) ─────────────────────────────────────────────
def full_node(state: AgentState, writer: StreamWriter):
    """
    Mode = full
    Order:
      1. intro_message  (stream)
      2. sql            (stream)
      3. sql_message    (stream)
      4. execute SQL    (blocking – emit result at once)
      5. analysis       (stream)
    """
    schema_text = get_db_schema_text()
    question    = state["question"]

    # ── 1. Intro message ──────────────────────────────────────────────────────
    writer({"type": "section_start", "node": "full", "section": "intro"})
    intro_text = ""
    for chunk in intro_chain.stream({"question": question}):
        token = chunk.content
        if token:
            intro_text += token
            writer({"type": "token", "node": "full", "section": "intro", "value": token})
    writer({"type": "section_end", "node": "full", "section": "intro"})

    # ── 2. SQL generation ─────────────────────────────────────────────────────
    writer({"type": "section_start", "node": "full", "section": "sql"})
    full_sql = ""
    for chunk in sql_chain.stream({"question": question, "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "full", "section": "sql", "value": token})
    writer({"type": "section_end", "node": "full", "section": "sql"})

    # ── 3. SQL explanation ────────────────────────────────────────────────────
    writer({"type": "section_start", "node": "full", "section": "sql_message"})
    sql_message_text = ""
    for chunk in sql_message_chain.stream({"question": question, "sql": full_sql}):
        token = chunk.content
        if token:
            sql_message_text += token
            writer({"type": "token", "node": "full", "section": "sql_message", "value": token})
    writer({"type": "section_end", "node": "full", "section": "sql_message"})

    # ── 4. Execute SQL (blocking) ─────────────────────────────────────────────
    query_result = run_sql_query(full_sql)
    writer({"type": "result", "node": "full", "section": "result", "value": query_result})

    # ── 5. Analysis (stream) ──────────────────────────────────────────────────
    writer({"type": "section_start", "node": "full", "section": "analysis"})
    analysis_text = ""
    for chunk in analyzer_chain.stream({"question": question, "sql": full_sql, "result": query_result}):
        token = chunk.content
        if token:
            analysis_text += token
            writer({"type": "token", "node": "full", "section": "analysis", "value": token})
    writer({"type": "section_end", "node": "full", "section": "analysis"})

    return {
        "sql":           full_sql,
        "result":        query_result,
        "intro_message": intro_text,
        "sql_message":   sql_message_text,
        "analysis":      analysis_text,
    }

# ─────────────────────────────────────────
# Graph
# ─────────────────────────────────────────
def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("intent", intent_node)
    builder.add_node("chat",   chat_node)
    builder.add_node("sql",    sql_node)
    builder.add_node("result", result_node)
    builder.add_node("full",   full_node)

    builder.set_entry_point("intent")

    builder.add_conditional_edges(
        "intent",
        router,
        {
            "chat":   "chat",
            "sql":    "sql",
            "result": "result",
            "full":   "full",
        },
    )

    builder.add_edge("chat",   END)
    builder.add_edge("sql",    END)
    builder.add_edge("result", END)
    builder.add_edge("full",   END)

    return builder.compile()

graph = build_graph()

# ─────────────────────────────────────────
# Runner
# ─────────────────────────────────────────
def run(question: str, streaming: bool = True):
    """
    Run the SQL agent graph.

    Parameters
    ----------
    question  : the user's question
    streaming : True  → yield / print token-by-token events (custom + updates)
                False → invoke the graph once and return the final state dict
    
    Returns
    -------
    streaming=True  → generator that yields (event_mode, event_data) tuples
    streaming=False → final AgentState dict
    """
    inputs = {"question": question}

    if streaming:
        # ── Streaming path ────────────────────────────────────────────────────
        # Nodes use StreamWriter → emits custom events token-by-token.
        # Caller can iterate the generator or just call run_and_print().
        def _event_generator():
            for event in graph.stream(inputs, stream_mode=["updates", "custom"]):
                yield event
        return _event_generator()

    else:
        # ── Non-streaming path ────────────────────────────────────────────────
        # graph.invoke() runs the graph to completion and returns the final state.
        # StreamWriter calls inside nodes are silently ignored (no-op) when the
        # graph is invoked without stream_mode, so no refactoring needed.
        final_state: AgentState = graph.invoke(inputs)
        return final_state


# ─────────────────────────────────────────
# Convenience print helper
# ─────────────────────────────────────────
def run_and_print(question: str, streaming: bool = True):
    """Run the graph and print results to stdout — useful for quick testing."""
    if streaming:
        for event_mode, event_data in run(question, streaming=True):
            if event_mode == "updates":
                print("[UPDATE]", event_data)
            elif event_mode == "custom":
                print("[CUSTOM]", event_data)
    else:
        final_state = run(question, streaming=False)
        print("[FINAL STATE]", final_state)


# ─────────────────────────────────────────
# Quick demo
# ─────────────────────────────────────────
if __name__ == "__main__":
    QUESTIONS = {
        "chat":   "سلام! می‌تونی درباره قابلیت‌های خودت توضیح بدی؟",
        "sql":    "فقط کوئری SQL برای گرفتن ۱۰ سفارش آخر بنویس.",
        "result": "نتیجه کوئری ده تا سفارش آخر رو بده.",
        "full":   "کدوم محصولات بیشترین فروش رو داشتن؟",
    }

    test_mode  = "full"
    do_stream  = True          # ← True = streaming,  False = non-streaming

    print(f"\n{'='*60}")
    print(f"Mode: {test_mode}  |  streaming={do_stream}")
    print(f"Question: {QUESTIONS[test_mode]}")
    print(f"{'='*60}\n")

    run_and_print(QUESTIONS[test_mode], streaming=do_stream)