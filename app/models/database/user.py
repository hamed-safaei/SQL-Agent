from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, nullable=False)

    sessions = relationship(
        "Session",
        back_populates="user"
    )