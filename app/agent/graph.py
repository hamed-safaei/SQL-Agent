from langgraph.graph import StateGraph, END

from app.agent.schemas.states  import AgentState
from app.agent.nodes import (
    intent_node,
    router,
    chat_node,
    sql_node,
    full_node,
    execute_sql_node,
    after_sql_router,
    analyzer_node,
)


#Graph

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("intent", intent_node)
    builder.add_node("chat", chat_node)
    builder.add_node("sql", sql_node)
    builder.add_node("full", full_node)
    builder.add_node("execute_sql", execute_sql_node)
    builder.add_node("analyzer", analyzer_node)

    builder.set_entry_point("intent")

    builder.add_conditional_edges(
        "intent",
        router,
        {
            "chat": "chat",
            "sql": "sql",
            "result": "sql",
            "full": "full"
        }
    )

    builder.add_conditional_edges(
        "sql",
        after_sql_router,
        {
            "execute": "execute_sql",
            "end": END
        }
    )

    builder.add_edge("full", "execute_sql")
    builder.add_edge("chat", END)
    builder.add_edge("execute_sql", "analyzer")
    builder.add_edge("analyzer", END)

    return builder.compile()


graph = build_graph()