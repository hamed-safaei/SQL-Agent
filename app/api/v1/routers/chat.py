from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.agent import graph
from app.core.database.database import get_app_db

from app.models.schemas import( 
UserChat , AssistantChat ,ChatRequest, ChatResponse ,
SessionInfo , Message
)
from app.repositories import (create_session,
    get_session_by_id,
    create_user_message,
    create_agent_message,
    )
from app.agent.schemas.states import build_metadata 
from app.api.v1.dependencies import get_authorized_session , get_jwt_auth_user


router = APIRouter(prefix="/chat", tags=["Chat"])



# def _get_authorized_session(db: Session, session_id: int, user_id: int):
#     session =  get_session_by_id(db, session_id)
#     if session is None:
#         raise HTTPException(status_code=404, detail="Session not found")
#     if session.user_id != user_id:
#         raise HTTPException(status_code=403, detail="Access denied")
#     return session


# ---------


# @router.post("/send", response_model=ChatResponse)
# def send_message(
#     req: ChatRequest,
#     db: Session = Depends(get_app_db),
#     current_user=Depends(get_jwt_auth_user)
# ):
#     if req.session_id is None:
#         session =  create_session(db, user_id=current_user.id)
#     else:
#         session = _get_authorized_session(db, req.session_id, current_user.id)

#     user_msg =  create_user_message(
#         db=db,
#         session_id=session.id,
#         content=req.content
#     )

#     agent_result = graph.invoke({"question": req.content})

#     agent_msg =  create_agent_message(
#         db=db,
#         session_id=session.id,
#         agent_metadata=build_metadata(agent_result)
#     )

#     return ChatResponse(
#         session=SessionInfo(
#             id=session.id,
#             title=session.title
#         ),
#         # user_message=UserChat.model_validate(user_msg),
#         assistant=AssistantChat.model_validate(agent_msg),
#         message = Message.model_validate(agent_msg)
#     )





@router.post("/send1", response_model=ChatResponse)
def send_message(
    req: ChatRequest,
    session=Depends(get_authorized_session),
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user),
):
    if session is None:
        session = create_session(
            db=db,
            user_id=current_user.id,
        )

    user_msg = create_user_message(
        db=db,
        session_id=session.id,
        content=req.content,
    )

    agent_result = graph.invoke(
        {"question": req.content}
    )

    agent_msg = create_agent_message(
        db=db,
        session_id=session.id,
        agent_metadata=build_metadata(agent_result),
    )

    return ChatResponse(
        session=SessionInfo(
            id=session.id,
            title=session.title,
        ),
        assistant=AssistantChat.model_validate(agent_msg),
        message=Message.model_validate(agent_msg),
    )
























import json
from typing import Optional, AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.st import run, AgentState

# ─────────────────────────────────────────
# Request model
# ─────────────────────────────────────────
class ChatRequest1(BaseModel):
    session_id: Optional[UUID] = Field(default=None, examples=[None])
    content:   str
    streaming: bool = Field(default=False, description="True → SSE stream, False → JSON")
# ─────────────────────────────────────────
# SSE helpers
# ─────────────────────────────────────────
def _default_serializer(obj):
    """Fallback serializer for types json.dumps cannot handle natively (UUID, datetime, Decimal …)."""
    import uuid, datetime, decimal
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
 
 
async def _stream_sse(
    question: str,
    session,
    db,
    create_agent_message_fn,
    build_metadata_fn,
) -> AsyncGenerator[str, None]:
    """
    Iterate the graph's streaming generator and forward each event as an SSE frame.
    After the graph finishes, persist the agent message and emit 'done'.
 
    SSE event types emitted:
    ┌─────────────────┬────────────────────────────────────────────────────────────┐
    │ event name      │ data payload                                               │
    ├─────────────────┼────────────────────────────────────────────────────────────┤
    │ intent          │ {mode}                                                     │
    │ token           │ {node, section?, value}                                    │
    │ section_start   │ {node, section}                                            │
    │ section_end     │ {node, section}                                            │
    │ result          │ {node, section?, value}                                    │
    │ done            │ {session: {id, title}, agent_msg_id}                       │
    └─────────────────┴────────────────────────────────────────────────────────────┘
    """
    # Accumulate the full graph state across all node updates.
    # Each "updates" event is a dict  {node_name: {fields_written_by_that_node}}.
    # Merging every node's output gives us the same final state that
    # graph.invoke() would return — which is exactly what build_metadata expects.
    final_state: dict = {"question": question}
 
    for event_mode, event_data in run(question, streaming=True):
 
        if event_mode == "updates":
            # Merge every node's output into final_state
            for node_output in event_data.values():
                if isinstance(node_output, dict):
                    final_state.update(node_output)
 
            # Emit intent event to the client after intent node runs
            if "intent" in event_data:
                yield _sse("intent", {"mode": event_data["intent"].get("mode")})
 
        elif event_mode == "custom":
            evt_type = event_data.get("type")
 
            if evt_type == "token":
                yield _sse("token", {
                    "node":    event_data.get("node"),
                    "section": event_data.get("section"),
                    "value":   event_data.get("value"),
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
                    "section": event_data.get("section"),
                    "value":   event_data.get("value"),
                })
 
    # ── Graph finished → persist agent message ────────────────────────────────
    agent_msg = create_agent_message_fn(
        db=db,
        session_id=session.id,
        agent_metadata=build_metadata_fn(final_state),
    )
 
    # ── Signal end of stream with agent msg id + session info ─────────────────
    yield _sse("done", {
        "session": {
            "id":    session.id,
            "title": session.title,
        },
        "agent_msg_id": agent_msg.id,
    })
 
 
# ─────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────
@router.post("/send")
def send_message(
    req: ChatRequest1,
    session=Depends(get_authorized_session),
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user),
):
    # ── Session & user message (same as before) ───────────────────────────────
    if session is None:
        session = create_session(db=db, user_id=current_user.id)
 
    user_msg = create_user_message(
        db=db,
        session_id=session.id,
        content=req.content,
    )
 
    # ─────────────────────────────────────────
    # Branch: streaming  vs  non-streaming
    # ─────────────────────────────────────────
    if req.streaming:
        # ── SSE path ─────────────────────────────────────────────────────────
        # We do NOT save the agent message here because the graph hasn't
        # finished yet — the client receives the "done" event when it's complete.
        # If you need to persist the message, do it inside the generator after
        # the loop (pass db / session via closure or a background task).
        return StreamingResponse(
            _stream_sse(
                question=req.content,
                session=session,
                db=db,
                create_agent_message_fn=create_agent_message,
                build_metadata_fn=build_metadata,
            ),
            media_type="text/event-stream",
            headers={
                # Prevent proxies / nginx from buffering the stream
                "Cache-Control":       "no-cache",
                "X-Accel-Buffering":   "no",
                "Connection":          "keep-alive",
            },
        )
 
    else:
        # ── Non-streaming path (identical logic to old endpoint) ──────────────
        agent_result: AgentState = run(req.content, streaming=False)
 
        agent_msg = create_agent_message(
            db=db,
            session_id=session.id,
            agent_metadata=build_metadata(agent_result),
        )
 
        return ChatResponse(
            session=SessionInfo(
                id=session.id,
                title=session.title,
            ),
            assistant=AssistantChat.model_validate(agent_msg),
            message=Message.model_validate(agent_msg),
        )