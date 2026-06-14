from sqlalchemy.orm import Session

from app.models.database.feedbacks import Feedback


def create_feedback(
    db: Session,
    user_id: int,
    message_id: int,
    rating: int,
    reason_code: str | None = None,
    comment: str | None = None,
) -> Feedback:

    feedback = Feedback(
        user_id=user_id,
        message_id=message_id,
        rating=rating,
        reason_code=reason_code,
        comment=comment,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return feedback