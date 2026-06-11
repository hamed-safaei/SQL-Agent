from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.agent import graph
from app.core.database import get_app_db
from app.auth.dependencies import get_jwt_auth_user

from app.models.schemas import( 
UserChat , AssistantChat ,ChatRequest, ChatResponse ,
SessionInfo
)
from app.repositories import (create_session,
    get_session_by_id,
    create_user_message,
    create_agent_message,
    )



router = APIRouter(prefix="/chat", tags=["chat"])



def _get_authorized_session(db: Session, session_id: int, user_id: int):
    session =  get_session_by_id(db, session_id)
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
        session =  create_session(db, user_id=current_user.id)
        is_new_session = True
    else:
        session = _get_authorized_session(db, req.session_id, current_user.id)

    user_msg =  create_user_message(
        db=db,
        session_id=session.id,
        content=req.content
    )

    agent_result = graph.invoke({"question": req.content})

    agent_msg =  create_agent_message(
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

