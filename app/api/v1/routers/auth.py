from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession
from datetime import timedelta , datetime

from app.core import get_app_db
from app.core.security import hash_password , verify_password , create_access_token , create_refresh_token

from app.models import schemas
from app import repositories
from app.repositories import token_repository





router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=schemas.UserRead)
def register(
    user: schemas.UserRegister,
    db: DBSession = Depends(get_app_db)
):
    existing_user = repositories.get_user_by_username(
        db,
        user.username
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = repositories.create_user(
        db=db,
        username=user.username,
        password_hash=hashed_password
    )

    return new_user







@router.post("/login")
def login(
    user: schemas.UserLogin,
    db: DBSession = Depends(get_app_db)
):
    db_user = repositories.get_user_by_username(db, user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # -------------------------
    # Access Token
    # -------------------------
    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    # -------------------------
    # Refresh Token
    # -------------------------
    refresh_token = create_refresh_token()

    token_repository.create_refresh_token_record(
        db=db,
        user_id=db_user.id,
        refresh_token=refresh_token,
        expires_days=7
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }







@router.post("/logout")
def logout(
    refresh_token: str,
    db: DBSession = Depends(get_app_db)
):
    repositories.revoke_token(db, refresh_token)

    return {"message": "Logged out successfully"}







from app.models.database import TokenModel
from datetime import datetime, timedelta, timezone
import secrets

def generate_token(length = 32):
    return secrets.token_hex(length)

expires_at = datetime.now(timezone.utc) + timedelta(days=7)

@router.post("/login2")
def login(
    user: schemas.UserLogin,
    db: DBSession = Depends(get_app_db)
):
    db_user = repositories.get_user_by_username(db, user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_obj = TokenModel(user_id = db_user.id , refresh_token = generate_token() , expires_at=expires_at , revoked=False)
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return JSONResponse (content = {"detail" : "logged in successfully" , "token": token_obj.refresh_token} )




from app.auth import generate_access_token , generate_refresh_token , decode_refresh_token


@router.post("/login3")
def login(
    user: schemas.UserLogin,
    db: DBSession = Depends(get_app_db)
):
    db_user = repositories.get_user_by_username(db, user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # token_obj = TokenModel(user_id = db_user.id , refresh_token = generate_token() , expires_at=expires_at , revoked=False)
    # db.add(token_obj)
    # db.commit()
    # db.refresh(token_obj)

    access_token = generate_access_token(db_user.id)
    refresh_token = generate_refresh_token(db_user.id)

    return JSONResponse (content = {"detail" : "logged in successfully" , "access_token": access_token , "refresh_token": refresh_token} )






@router.post("/refresh")
def refresh_token(
    request: schemas.UserRefreshToken ,
    db: DBSession = Depends(get_app_db)
):
        
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)

    return JSONResponse (content = { "access_token": access_token } )
