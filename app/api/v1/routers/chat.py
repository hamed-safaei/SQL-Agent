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





@router.post("/send", response_model=ChatResponse)
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









