from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_app_db
from app.auth.dependencies import get_jwt_auth_user
from app.models.schemas.chat import ChatRequest, ChatResponse
from app.models.schemas.session import SessionSummary , SessionTitleUpdate , SessionInfo
from app.models.schemas.message import MessageRead
from app.models.schemas.chat import UserChat , AssistantChat
from uuid import UUID


import app.repositories.session_repository as session_repo
import app.repositories.message_repository as message_repo

from app.agent import graph

router = APIRouter(prefix="/chat", tags=["chat"])



def _get_authorized_session(db: Session, session_id: int, user_id: int):
    session = session_repo.get_session_by_id(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return session


# ---------


@router.post("/send", response_model=ChatResponse)
def send_message(
    req: ChatRequest,
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user)
):
    is_new_session = False
    if req.session_id is None:
        session = session_repo.create_session(db, user_id=current_user.id)
        is_new_session = True
    else:
        session = _get_authorized_session(db, req.session_id, current_user.id)

    user_msg = message_repo.create_user_message(
        db=db,
        session_id=session.id,
        content=req.content
    )

    agent_result = graph.invoke({"question": req.content})

    agent_msg = message_repo.create_agent_message(
        db=db,
        session_id=session.id,
        agent_metadata=agent_result
    )

    return ChatResponse(
        session=SessionInfo(
            id=session.id,
            title=session.title,
            is_new=is_new_session
        ),
        user_message=UserChat.model_validate(user_msg),
        agent_message=AssistantChat.model_validate(agent_msg),
    )


# ---------


@router.get("/sessions", response_model=list[SessionSummary])
def get_user_sessions(
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user)
):
    return session_repo.get_sessions_by_user_id(db, current_user.id)



# ---------


@router.get("/sessions/{session_id}", response_model=list[MessageRead])
def get_session_messages(
    session_id: UUID,
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user)
):
    _get_authorized_session(db, session_id, current_user.id)
    return message_repo.get_messages_by_session_id(db, session_id)


# ---------



@router.patch("/sessions/{session_id}/title", response_model=SessionSummary)
def update_session_title(
    session_id: UUID,
    body: SessionTitleUpdate,
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user)
):
    _get_authorized_session(db, session_id, current_user.id)
    updated = session_repo.update_session_title(db, session_id, body.title)
    return updated



# ---------



@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user)
):
    _get_authorized_session(db, session_id, current_user.id)
    session_repo.delete_session(db, session_id)