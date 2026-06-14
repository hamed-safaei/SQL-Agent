from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session

from app.core.database import get_app_db
from app.api.v1.dependencies import get_jwt_auth_user
from app.models.schemas import (
    FeedbackCreate,
    FeedbackResponse,
)

from app.repositories import (
    create_feedback,
)

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


@router.post(
    "",
    # response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,

)
def add_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_app_db),
    current_user=Depends(get_jwt_auth_user),
):

    feedback = create_feedback(
        db=db,
        user_id=current_user.id,
        message_id=data.message_id,
        rating=data.rating,
        reason_code=data.reason_code,
        comment=data.comment,
    )

    return {
        "detail" : "Feedback added successfully"
    }