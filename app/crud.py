# app/crud.py
from __future__ import annotations

from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, update , delete

from app.models.tables import User, Session as ChatSession, Message


# -------------------------
# Users
# -------------------------
def create_user(db: Session, username: str) -> User:
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    return db.execute(stmt).scalar_one_or_none()


def list_users(db: Session, limit: int = 100, offset: int = 0) -> Sequence[User]:
    stmt = select(User).order_by(User.id).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# -------------------------
# Sessions
# -------------------------
def create_session(
    db: Session,
    user_id: int,
    *,
    is_active: bool = True,
    deactivate_others: bool = True,
) -> ChatSession:
    """
    یک Session جدید برای user می‌سازد.
    اگر deactivate_others=True باشد، سشن‌های فعال قبلی همان user را غیرفعال می‌کند.
    """
    if deactivate_others:
        stmt = (
            update(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.is_active.is_(True))
            .values(is_active=False)
        )
        db.execute(stmt)

    s = ChatSession(user_id=user_id, is_active=is_active)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s



def get_and_activate_session(db: Session, user_id: int, session_id: int) -> Optional[ChatSession]:
    db_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

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



def get_active_session_for_user(db: Session, user_id: int) -> Optional[ChatSession]:
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id, ChatSession.is_active.is_(True))
        .order_by(ChatSession.created_at.desc(), ChatSession.id.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_sessions_for_user(
    db: Session, user_id: int, limit: int = 100, offset: int = 0
) -> Sequence[ChatSession]:
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc(), ChatSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()



def delete_session_by_id(db: Session, user_id: int, session_id: int) -> bool:
    db_session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id
    ).first()

    if not db_session:
        return False

    # ۲. حذف پیام‌های مربوط به این سشن
    # (اگر در دیتابیس CASCADE ست نکرده باشید، این مرحله الزامی است)
    db.execute(delete(Message).where(Message.session_id == session_id))

    # ۳. حذف خودِ سشن
    db.delete(db_session)
    
    # ۴. نهایی کردن تغییرات
    db.commit()
    return True

# -------------------------
# Messages
# -------------------------
def create_message(db: Session, session_id: int, role: str, content: str = None, agent_metadata: dict = None):
    new_message = Message(
        session_id=session_id,
        role=role,
        content=content,
        agent_metadata=agent_metadata
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message



def get_messages_for_active_session(db: Session, user_id: int):
    # ۱. پیدا کردن سشن فعال
    active_session = get_active_session_for_user(db, user_id)
    if not active_session:
        return [] # یا می‌توانید None برگردانید

    # ۲. گرفتن تمام پیام‌های این سشن به ترتیب زمان
    messages = db.query(Message).filter(
        Message.session_id == active_session.id
    ).order_by(Message.created_at.asc()).all()
    
    return messages


