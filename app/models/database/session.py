from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Boolean
)

from sqlalchemy.orm import relationship
from datetime import datetime

from app.appdb import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    is_active = Column(
        Boolean,
        default=True
    )

    user = relationship(
        "User",
        back_populates="sessions"
    )

    messages = relationship(
        "Message",
        back_populates="session"
    )