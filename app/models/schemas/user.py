from pydantic import BaseModel, ConfigDict
from app.models.schemas.session import Session


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserWithSessions(UserRead):
    sessions: list[Session] = []



# ///////////////////////////


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRefreshToken(BaseModel):
    token: str
