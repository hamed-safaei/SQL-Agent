# from typing import Optional, Sequence
# from sqlalchemy import (
#     select,
#     update,
#     delete
# )

# from sqlalchemy.orm import Session
# from app.models.database import (
#     Session as ChatSession,
#     Message
# )





# def create_session(
#     db: Session,
#     user_id: int,
# ) -> ChatSession:

#     session = ChatSession(
#         user_id=user_id
#     )

#     db.add(session)
#     db.commit()
#     db.refresh(session)

#     return session





# def get_user_sessions(
#     db: Session,
#     user_id: int
# ):
#     return db.query(ChatSession).filter(
#         ChatSession.user_id == user_id
#     ).all()





# def delete_session_by_id(
#     db: Session,
#     user_id: int,
#     session_id: int
# ) -> bool:

#     db_session = (
#         db.query(ChatSession)
#         .filter(
#             ChatSession.id == session_id,
#             ChatSession.user_id == user_id
#         )
#         .first()
#     )

#     if not db_session:
#         return False

#     db.execute(
#         delete(Message)
#         .where(Message.session_id == session_id)
#     )

#     db.delete(db_session)

#     db.commit()

#     return True



from sqlalchemy.orm import Session
from app.models.database.session import Session as SessionModel
from app.models.database.message import Message


def create_session(db: Session, user_id: int) -> SessionModel:
    new_session = SessionModel(
        user_id=user_id,
        title="text"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def get_session_by_id(db: Session, session_id: int) -> SessionModel | None:
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_sessions_by_user_id(db: Session, user_id: int) -> list[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
        .all()
    )


def update_session_title(
    db: Session,
    session_id: int,
    new_title: str
) -> SessionModel:
    session = get_session_by_id(db, session_id)
    session.title = new_title
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: int) -> None:
    # اول پیام های مرتبط حذف می‌شوند
    db.query(Message).filter(Message.session_id == session_id).delete()
    db.query(SessionModel).filter(SessionModel.id == session_id).delete()
    db.commit()