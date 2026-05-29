from fastapi import FastAPI, HTTPException , Query , Depends , status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.agent import run_ai_agent_stream
import uvicorn
from fastapi_swagger import patch_fastapi
from contextlib import asynccontextmanager
import asyncpg
import asyncio
from app.graph import graph
from app.appdb import Base, app_engine ,get_app_db
from app.models.tables import User, Session, Message 
from sqlalchemy.orm import Session as DBSession
from app.models import schemas
from app import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> Running lifespan startup...")
    Base.metadata.create_all(bind=app_engine)
    print(">>> Database tables created!")
    yield
    print(">>> App shutting down...")

app = FastAPI(
    lifespan=lifespan,   
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None,
)
patch_fastapi(app, docs_url="/swagger")


# app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.get("/")
# async def get_index():
#     return FileResponse('static/index.html')



# //////////////////////////////////////////////////

@app.post("/users", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: DBSession = Depends(get_app_db)):
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return crud.create_user(db=db, username=user.username)


@app.get("/users/search", response_model=schemas.UserWithSessions)
def get_user(
    username: str = Query(..., alias="name", description="Username"),
    db: DBSession = Depends(get_app_db),
):
    db_user = crud.get_user_by_username(db, username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



@app.get("/users")
def list_users(skip: int = 0, limit: int = 100, db: DBSession = Depends(get_app_db)):
    return crud.list_users(db, offset=skip, limit=limit)



# ////////////////////////////////////////////////////////////



@app.post("/sessions", response_model=schemas.Session)
def create_session(
    session_data: schemas.SessionCreate,
    db: DBSession = Depends(get_app_db)
):
    # ۱. اطمینان از وجود کاربر
    user = crud.get_user_by_id(db, session_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return crud.create_session(
        db, 
        user_id=session_data.user_id, 
        deactivate_others=True
    )


@app.get("/sessions/{session_id}", response_model=schemas.Session)
def read_session(
    session_id: int, 
    user_id: int, 
    db: DBSession = Depends(get_app_db)
):
    db_session = crud.get_and_activate_session(db, user_id=user_id, session_id=session_id)
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or does not belong to this user"
        )
    
    return db_session



@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: int, 
    user_id: int, 
    db: DBSession = Depends(get_app_db)
):
    success = crud.delete_session_by_id(db, user_id=user_id, session_id=session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or you don't have permission to delete it"
        )
    
    # در متد 204 نباید بدنه (body) برگردانیم، پس فقط برمی‌گردیم
    return None




# //////////////////////////////////////////////////////////////



@app.post("/test-connection")
async def test_connection(conn: schemas.ConnectionTest):
    dsn = f"postgresql://{"hamed"}:{"1234"}@{conn.server}:{"5432"}/{conn.database}"

    try:
        connection = await asyncio.wait_for(
            asyncpg.connect(dsn),
            timeout=5.0
        )
        await connection.close()
        return {
            "success": True,
            "message": "اتصال با موفقیت برقرار شد ✓"
        }

    except asyncio.TimeoutError:
        return {"success": False, "message": "خطا: زمان اتصال به پایان رسید. سرور در دسترس نیست."}
    except asyncpg.InvalidCatalogNameError:
        return {"success": False, "message": "خطا: دیتابیس یافت نشد."}
    except asyncpg.InvalidAuthorizationSpecificationError:
        return {"success": False, "message": "خطا: نام کاربری یا رمز عبور اشتباه است."}
    except Exception as e:
        return {"success": False, "message": f"خطا در اتصال: {str(e)}"}


# //////////////////////////////////////////////////////////////


@app.post("/ask-stream")
def ask_agent_stream(req: schemas.QueryRequest):
    return StreamingResponse(
        run_ai_agent_stream(req.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )



@app.post("/ask")
def ask_agent(req: schemas.QueryRequest):
    result = graph.invoke({"question": req.question})
    return result

# //////////////////////////////////////////////////////////////


@app.post("/chat")
def chat_with_agent(req: schemas.MessageCreate, db: DBSession = Depends(get_app_db)):
    active_session = crud.get_active_session_for_user(db, req.user_id)
    if not active_session:
        raise HTTPException(status_code=404, detail="No active session found for this user")

    user_message = crud.create_message(
        db, 
        session_id=active_session.id, 
        role="user", 
        content=req.content
    )

    graph_result = graph.invoke({"question": req.content})
    
    assistant_message = crud.create_message(
        db, 
        session_id=active_session.id, 
        role="assistant", 
        content=None,          
        agent_metadata=graph_result 
    )

    return {
        "status": "success",
        "user_message_id": user_message.id,
        "assistant_message_id": assistant_message.id,
        "assistant_data": graph_result 
    }



@app.get("/chat/history/{user_id}", response_model=list[schemas.MessageRead])
def get_chat_history(user_id: int, db: DBSession = Depends(get_app_db)):
    messages = crud.get_messages_for_active_session(db, user_id)
    
    if messages is None:
         raise HTTPException(status_code=404, detail="No active session found for this user")
         
    return messages



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
