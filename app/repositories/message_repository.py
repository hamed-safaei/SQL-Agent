# from sqlalchemy.orm import Session

# from app.models.database import Message

# # from .session_repository import (
# #     get_active_session_for_user
# # )


# def create_message(
#     db: Session,
#     session_id: int,
#     role: str,
#     content: str = None,
#     agent_metadata: dict = None
# ):

#     message = Message(
#         session_id=session_id,
#         role=role,
#         content=content,
#         agent_metadata=agent_metadata
#     )

#     db.add(message)
#     db.commit()
#     db.refresh(message)

#     return message


# # def get_messages_for_active_session(
# #     db: Session,
# #     user_id: int
# # ):

# #     active_session = get_active_session_for_user(
# #         db,
# #         user_id
# #     )

# #     if not active_session:
# #         return []

# #     messages = (
# #         db.query(Message)
# #         .filter(
# #             Message.session_id == active_session.id
# #         )
# #         .order_by(Message.created_at.asc())
# #         .all()
# #     )

# #     return messages
import math
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.database.message import Message


def _make_json_serializable(obj):
    """
    بازگشتی تمام مقادیر غیر JSON-serializable رو تبدیل می‌کند.
    Decimal → float / int
    """
    if isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_serializable(i) for i in obj]
    if isinstance(obj, Decimal):
        # اگر عدد صحیح بود int برگردان، وگرنه float
        return int(obj) if obj == obj.to_integral_value() else float(obj)
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def create_user_message(
    db: Session,
    session_id: int,
    content: str
) -> Message:
    message = Message(
        session_id=session_id,
        role="user",
        content=content,
        agent_metadata=None
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_agent_message(
    db: Session,
    session_id: int,
    agent_metadata: dict
) -> Message:
    message = Message(
        session_id=session_id,
        role="assistant",
        content=None,
        agent_metadata=_make_json_serializable(agent_metadata)
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_by_session_id(db: Session, session_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .all()
    )