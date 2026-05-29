from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.core import get_app_db
from app.models import schemas
from app import repositories

router = APIRouter(
    prefix="/sessions",
    tags=["Session"]
)


@router.post("", response_model=schemas.Session)
def create_session(
    session_data: schemas.SessionCreate,
    db: DBSession = Depends(get_app_db)
):
    user = repositories.get_user_by_id(db, session_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return repositories.create_session(
        db,
        user_id=session_data.user_id,
        deactivate_others=True
    )


@router.get("/{session_id}", response_model=schemas.Session)
def read_session(
    session_id: int,
    user_id: int,
    db: DBSession = Depends(get_app_db)
):
    db_session = repositories.get_and_activate_session(
        db,
        user_id=user_id,
        session_id=session_id
    )

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to this user"
        )

    return db_session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: int,
    user_id: int,
    db: DBSession = Depends(get_app_db)
):
    success = repositories.delete_session_by_id(
        db,
        user_id=user_id,
        session_id=session_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or you don't have permission to delete it"
        )

    return None