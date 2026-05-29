from typing import Dict, List, Any
from app.models.states  import AgentState
from app.agent.chains import (
    intent_chain,
    chat_chain,
    sql_chain,
    full_chain,
    analyzer_chain,
)
from app.clientdb import get_db_schema_text , run_sql_query


#Nodes

def intent_node(state: AgentState):
    result = intent_chain.invoke({"question": state["question"]})
    return {"mode": result.mode}


def router(state: AgentState):
    return state["mode"]


def chat_node(state: AgentState):
    result = chat_chain.invoke({"question": state["question"]})
    return {"message": result.message}


def sql_node(state: AgentState):
    schema_text = get_db_schema_text()
    result = sql_chain.invoke({
        "question": state["question"],
        "schema": schema_text
    })
    return {"sql": result.sql}


def full_node(state: AgentState):
    schema_text = get_db_schema_text()
    result = full_chain.invoke({
        "question": state["question"],
        "schema": schema_text
    })
    return {
        "intro_message": result.intro_message,
        "sql": result.sql,
        "sql_message": result.sql_message
    }


def execute_sql_node(state: AgentState):
    try:
        rows = run_sql_query(state["sql"])
        return {"result": rows, "error": None}
    except Exception as e:
        return {"result": None, "error": str(e)}


def after_sql_router(state: AgentState):
    if state.get("mode") == "result":
        return "execute"
    else:
        return "end"


def analyzer_node(state: AgentState):
    analysis_result = analyzer_chain.invoke({
        "question": state["question"],
        "sql": state["sql"],
        "result": state["result"]
    })
    return {"analysis": analysis_result.analysis}