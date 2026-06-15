# from typing import Dict, List, Any
# from app.agent.schemas.states  import AgentState
# from app.agent.chains import (
#     intent_chain,
#     chat_chain,
#     sql_chain,
#     full_chain,
#     analyzer_chain,
# )


# #Nodes

# def intent_node(state: AgentState):
#     result = intent_chain.invoke({"question": state["question"]})
#     return {"mode": result.mode}


# def router(state: AgentState):
#     return state["mode"]


# def chat_node(state: AgentState):
#     result = chat_chain.invoke({"question": state["question"]})
#     return {"message": result.message}


# def sql_node(state: AgentState):
#     schema_text = get_db_schema_text()
#     result = sql_chain.invoke({
#         "question": state["question"],
#         "schema": schema_text
#     })
#     return {"sql": result.sql}


# def full_node(state: AgentState):
#     schema_text = get_db_schema_text()
#     result = full_chain.invoke({
#         "question": state["question"],
#         "schema": schema_text
#     })
#     return {
#         "intro_message": result.intro_message,
#         "sql": result.sql,
#         "sql_message": result.sql_message
#     }


# def execute_sql_node(state: AgentState):
#     try:
#         rows = run_sql_query(state["sql"])
#         return {"result": rows, "error": None}
#     except Exception as e:
#         return {"result": None, "error": str(e)}


# def after_sql_router(state: AgentState):
#     if state.get("mode") == "result":
#         return "execute"
#     else:
#         return "end"


# def analyzer_node(state: AgentState):
#     analysis_result = analyzer_chain.invoke({
#         "question": state["question"],
#         "sql": state["sql"],
#         "result": state["result"]
#     })
#     return {"analysis": analysis_result.analysis}











from typing import Any

from langgraph.types import StreamWriter

from .schemas.states.agent_state import AgentState
from .chains import (
    intent_chain,
    chat_chain,
    sql_chain,
    intro_chain,
    sql_message_chain,
    analyzer_chain,
)
from app.core.database.clientdb import get_db_schema_text , run_sql_query

# ── Helpers (replace stubs with real implementations) ─────────────────────────

# def get_db_schema_text() -> str:
#     """Return the database schema as plain text."""
#     # TODO: replace with your real schema loader
#     return """
#     TABLE users (id SERIAL PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP);
#     TABLE orders (id SERIAL PRIMARY KEY, user_id INT REFERENCES users(id), total NUMERIC, created_at TIMESTAMP);
#     TABLE products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC, stock INT);
#     TABLE order_items (id SERIAL PRIMARY KEY, order_id INT REFERENCES orders(id), product_id INT REFERENCES products(id), quantity INT);
#     """

# def run_sql_query(sql: str) -> Any:
#     """Execute the SQL and return the result."""
#     # TODO: replace with your real DB executor
#     return [{"id": 1, "name": "Alice", "total": 250.0}]


# ── Intent (no streaming) ─────────────────────────────────────────────────────

def intent_node(state: AgentState):
    result = intent_chain.invoke({"question": state["question"]})
    return {"mode": result.mode}


def router(state: AgentState) -> str:
    return state["mode"]


# ── Chat ──────────────────────────────────────────────────────────────────────

def chat_node(state: AgentState, writer: StreamWriter):
    full_message = ""
    for chunk in chat_chain.stream({"question": state["question"]}):
        token = chunk.content
        if token:
            full_message += token
            writer({"type": "token", "node": "chat", "value": token})
    return {"message": full_message}


# ── SQL only ──────────────────────────────────────────────────────────────────

def sql_node(state: AgentState, writer: StreamWriter):
    schema_text = get_db_schema_text()
    full_sql = ""
    for chunk in sql_chain.stream({"question": state["question"], "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "sql", "value": token})
    return {"sql": full_sql}


# ── Result (sql stream → blocking execute) ────────────────────────────────────

def result_node(state: AgentState, writer: StreamWriter):
    schema_text = get_db_schema_text()

    full_sql = ""
    for chunk in sql_chain.stream({"question": state["question"], "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "sql", "value": token})

    query_result = run_sql_query(full_sql)
    writer({"type": "result", "node": "result", "value": query_result})

    return {"sql": full_sql, "result": query_result}


# ── Full (multi-step stream) ──────────────────────────────────────────────────

def full_node(state: AgentState, writer: StreamWriter):
    """
    Order:
      1. intro_message  (stream)
      2. sql            (stream)
      3. sql_message    (stream)
      4. execute SQL    (blocking)
      5. analysis       (stream)
    """
    schema_text = get_db_schema_text()
    question    = state["question"]

    # 1. Intro
    writer({"type": "section_start", "node": "full", "section": "intro"})
    intro_text = ""
    for chunk in intro_chain.stream({"question": question}):
        token = chunk.content
        if token:
            intro_text += token
            writer({"type": "token", "node": "full", "section": "intro", "value": token})
    writer({"type": "section_end", "node": "full", "section": "intro"})

    # 2. SQL
    writer({"type": "section_start", "node": "full", "section": "sql"})
    full_sql = ""
    for chunk in sql_chain.stream({"question": question, "schema": schema_text}):
        token = chunk.content
        if token:
            full_sql += token
            writer({"type": "token", "node": "full", "section": "sql", "value": token})
    writer({"type": "section_end", "node": "full", "section": "sql"})

    # 3. SQL explanation
    writer({"type": "section_start", "node": "full", "section": "sql_message"})
    sql_message_text = ""
    for chunk in sql_message_chain.stream({"question": question, "sql": full_sql}):
        token = chunk.content
        if token:
            sql_message_text += token
            writer({"type": "token", "node": "full", "section": "sql_message", "value": token})
    writer({"type": "section_end", "node": "full", "section": "sql_message"})

    # 4. Execute SQL (blocking)
    query_result = run_sql_query(full_sql)
    writer({"type": "result", "node": "full", "section": "result", "value": query_result})

    # 5. Analysis
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