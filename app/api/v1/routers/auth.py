from fastapi import APIRouter, Depends , Request
from sqlalchemy.orm import Session as DBSession

from app.core import get_app_db
from app.models import schemas
from app.auth import (
    register_user,
    login_token,
    login_jwt,
    refresh_access_token ,
    logout_user
)
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post(
    "/register",
    response_model=schemas.UserRead
)
def register(
    user: schemas.UserRegister,
    db: DBSession = Depends(get_app_db)
):
    return register_user(
        db,
        user.username,
        user.password
    )


# @router.post("/login/token")
# def login_token_route(
#     user: schemas.UserLogin,
#     db: DBSession = Depends(get_app_db)
# ):
#     return login_token(
#         db,
#         user.username,
#         user.password
#     )


@router.post("/login/jwt")
def login_jwt_route(
    user: schemas.UserLogin,
    db: DBSession = Depends(get_app_db)
):
    return login_jwt(
        db,
        user.username,
        user.password
    )


@router.post("/logout")
def logout_route(
    request: Request,
    db: DBSession = Depends(get_app_db)
):
    return logout_user(
        request=request,
        db=db
    )


# @router.post("/refresh")
# def refresh_token_route(
#     request: schemas.UserRefreshToken
# ):
#     return refresh_access_token(
#         request.token
#     )



@router.post("/refresh")
def refresh_token_route(
    request: Request,
    db: DBSession = Depends(get_app_db)
):
    return refresh_access_token(
        request=request,
        db=db
    )