from typing import Optional, Sequence

from sqlalchemy import (
    select,
    update,
    delete
)

from sqlalchemy.orm import Session

from app.models.database import (
    Session as ChatSession,
    Message
)


def create_session(
    db: Session,
    user_id: int,
    *,
    is_active: bool = True,
    deactivate_others: bool = True,
) -> ChatSession:

    if deactivate_others:
        stmt = (
            update(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_active.is_(True)
            )
            .values(is_active=False)
        )

        db.execute(stmt)

    session = ChatSession(
        user_id=user_id,
        is_active=is_active
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_and_activate_session(
    db: Session,
    user_id: int,
    session_id: int
) -> Optional[ChatSession]:

    db_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not db_session:
        return None

    db.execute(
        update(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.id != session_id
        )
        .values(is_active=False)
    )

    if not db_session.is_active:
        db_session.is_active = True

    db.commit()
    db.refresh(db_session)

    return db_session


def get_active_session_for_user(
    db: Session,
    user_id: int
) -> Optional[ChatSession]:

    stmt = (
        select(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.is_active.is_(True)
        )
        .order_by(
            ChatSession.created_at.desc(),
            ChatSession.id.desc()
        )
        .limit(1)
    )

    return db.execute(stmt).scalar_one_or_none()


def list_sessions_for_user(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> Sequence[ChatSession]:

    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(
            ChatSession.created_at.desc(),
            ChatSession.id.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    return db.execute(stmt).scalars().all()


def delete_session_by_id(
    db: Session,
    user_id: int,
    session_id: int
) -> bool:

    db_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
        .first()
    )

    if not db_session:
        return False

    db.execute(
        delete(Message)
        .where(Message.session_id == session_id)
    )

    db.delete(db_session)

    db.commit()

    return True