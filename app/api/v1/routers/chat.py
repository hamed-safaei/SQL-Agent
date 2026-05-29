from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.appdb import get_app_db
from app.models import schemas
from app import crud
from app.graph import graph

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("")
def chat_with_agent(
    req: schemas.MessageCreate,
    db: DBSession = Depends(get_app_db)
):
    active_session = crud.get_active_session_for_user(db, req.user_id)

    if not active_session:
        raise HTTPException(
            status_code=404,
            detail="No active session found for this user"
        )

    user_message = crud.create_message(
        db,
        session_id=active_session.id,
        role="user",
        content=req.content
    )

    graph_result = graph.invoke({"question": req.content})

    assistant_message = crud.create_message(
        db,
        session_id=active_session.id,
        role="assistant",
        content=None,
        agent_metadata=graph_result
    )

    return {
        "status": "success",
        "user_message_id": user_message.id,
        "assistant_message_id": assistant_message.id,
        "assistant_data": graph_result
    }


@router.get("/history/{user_id}", response_model=list[schemas.MessageRead])
def get_chat_history(
    user_id: int,
    db: DBSession = Depends(get_app_db)
):
    messages = crud.get_messages_for_active_session(db, user_id)

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="No active session found for this user"
        )

    return messages