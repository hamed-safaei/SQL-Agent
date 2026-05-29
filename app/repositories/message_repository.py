from sqlalchemy.orm import Session

from app.models.database import Message

from .session_repository import (
    get_active_session_for_user
)


def create_message(
    db: Session,
    session_id: int,
    role: str,
    content: str = None,
    agent_metadata: dict = None
):

    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        agent_metadata=agent_metadata
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages_for_active_session(
    db: Session,
    user_id: int
):

    active_session = get_active_session_for_user(
        db,
        user_id
    )

    if not active_session:
        return []

    messages = (
        db.query(Message)
        .filter(
            Message.session_id == active_session.id
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages