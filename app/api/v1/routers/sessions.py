from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session as DBSession
from app.auth import get_jwt_auth_user
from app.models.database import User
from app.core import get_app_db
from app.models import schemas
from app import repositories

router = APIRouter(
    prefix="/sessions",
    tags=["Session"]
)




# @router.post("", response_model=schemas.SessionsRead)
# def create_session(
#     user: User = Depends(get_jwt_auth_user),
#     db: DBSession = Depends(get_app_db)
# ):
#     return repositories.create_session(
#         db,
#         user_id=user.id
#     )




# @router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_chat_session(
#     session_id: int,
#     user_id: int,
#     db: DBSession = Depends(get_app_db)
# ):
#     success = repositories.delete_session_by_id(
#         db,
#         user_id=user_id,
#         session_id=session_id
#     )

#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Session not found or you don't have permission to delete it"
#         )

#     return None




# @router.get("/")
# def get_my_sessions(
#     user: User = Depends(get_jwt_auth_user),
#     db: DBSession = Depends(get_app_db)
# ):
#     sessions = repositories.get_user_sessions(
#         db,
#         user_id=user.id
#     )

#     return sessions
