import json
import uuid
import datetime
import decimal
from typing import AsyncGenerator

from app.agent.agent import run
from app.agent.schemas.states.agent_state import AgentState
from app.agent.schemas.states.metadata_mappers import build_metadata


# JSON serializer
def _default_serializer(obj):
    """Fallback for types json.dumps cannot handle (UUID, datetime, Decimal)."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _sse(event: str, data: dict) -> str:
    """Format a single SSE frame."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=_default_serializer)}\n\n"


async def stream_chat_sse(
    question: str,
    session,
    db,
    create_agent_message_fn,
) -> AsyncGenerator[str, None]:

    yield _sse("session", {
        "id":    session.id,
        "title": session.title,
    })


    final_state: dict = {"question": question}

    for event_mode, event_data in run(question, streaming=True):

        if event_mode == "updates":
            for node_output in event_data.values():
                if isinstance(node_output, dict):
                    final_state.update(node_output)

            if "intent" in event_data:
                yield _sse("intent", {"mode": event_data["intent"].get("mode")})

        elif event_mode == "custom":
            evt_type = event_data.get("type")

            if evt_type == "token":
                yield _sse("token", {
                    "node":  event_data.get("node"),
                    "value": event_data.get("value"),
                })

            elif evt_type == "section_start":
                yield _sse("section_start", {
                    "node":    event_data.get("node"),
                    "section": event_data.get("section"),
                })

            elif evt_type == "section_end":
                yield _sse("section_end", {
                    "node":    event_data.get("node"),
                    "section": event_data.get("section"),
                })

            elif evt_type == "result":
                yield _sse("result", {
                    "node":    event_data.get("node"),
                    # "section": event_data.get("section"),
                    "value":   event_data.get("value"),
                })


    agent_msg = create_agent_message_fn(
        db=db,
        session_id=session.id,
        agent_metadata=build_metadata(final_state),
    )


    yield _sse("message", {"agent_msg_id": agent_msg.id})



# Non-streaming handler
def run_chat_sync(
    question: str,
    session,
    db,
    create_agent_message_fn,
    build_metadata_fn,
    response_builder_fn,
):

    agent_result: AgentState = run(question, streaming=False)

    agent_msg = create_agent_message_fn(
        db=db,
        session_id=session.id,
        agent_metadata=build_metadata_fn(agent_result),
    )

    return response_builder_fn(session=session, agent_msg=agent_msg)
















    """
    Runs the agent graph in streaming mode and yields SSE frames.

    SSE event order:
    ┌──────────────┬──────────────────────────────────────────────┐
    │ event        │ payload                                      │
    ├──────────────┼──────────────────────────────────────────────┤
    │ session      │ {id, title}      ← first, before graph      │
    │ intent       │ {mode}                                       │
    │ token        │ {node, value}                                │
    │ section_start│ {node, section}                              │
    │ section_end  │ {node, section}                              │
    │ result       │ {node, section, value}                       │
    │ message      │ {agent_msg_id}   ← last                      │
    └──────────────┴──────────────────────────────────────────────┘
    """