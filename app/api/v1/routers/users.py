# from fastapi import APIRouter, HTTPException, Query, Depends
# from sqlalchemy.orm import Session as DBSession
# from typing import List
# from app.core import get_app_db
# from app.models import schemas
# from app import repositories

# router = APIRouter(
#     prefix="/users",
#     tags=["User"]
# )

# @router.get("/search", response_model=schemas.UserWithSessions)
# def get_user(
#     username: str = Query(..., alias="name", description="Username"),
#     db: DBSession = Depends(get_app_db),
# ):
#     db_user = repositories.get_user_by_username(db, username)

#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     return db_user




# @router.get("" , response_model = List[schemas.UserRead])
# def list_users(
#     skip: int = 0,
#     limit: int = 100,
#     db: DBSession = Depends(get_app_db)
# ):
#     return repositories.list_users(db, offset=skip, limit=limit)