from fastapi import FastAPI , Depends , Response , Request
from contextlib import asynccontextmanager
import uvicorn
from fastapi_swagger import patch_fastapi
from app.core import Base, app_engine
from app.api import api_router
from app.auth import get_current_username , get_auth_user 
from app.api.v1.dependencies import get_jwt_auth_user
from app.models.database import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> Running lifespan startup...")
    yield
    print(">>> App shutting down...")


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None,
)



patch_fastapi(app, docs_url="/swagger")
app.include_router(api_router)




@app.get("/public")
def public_route():
    return {"message" : "This is a public route"}


# @app.get("/private/basic")
# def private_route(user : User = Depends(get_current_username)):
#     print(user.username)
#     return {"message" : "This is a private route"}


# @app.get("/private/token")
# def private_route(user = Depends(get_auth_user)):
#     print(user.username)
#     return {"message" : "This is a private route"}


@app.get("/private/token/jwt")
def private_route(user = Depends(get_jwt_auth_user)):
    print(user.id)
    return {"message" : "This is a private route"}



# @app.post("/set-cookie")
# def create_cookie(response: Response):
#     response.set_cookie(key="test", value="something")
#     return {"message": "Cookie Has Been Set"}


# @app.get("/get-cookie")
# def get_cookie(request: Request):
#     print(request.cookies.get('test'))
#     return {"message": "Cookie Has Been Set"}

from fastapi import FastAPI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid



# اتصال به Qdrant
client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "test_collection"


# ساخت collection اگر نبود
def create_collection():
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=4,  # چون embedding fake می‌سازیم
                distance=Distance.COSINE
            )
        )


create_collection()


# یک embedding fake برای تست
def fake_embedding(text: str):
    # فقط برای تست (واقعی نیست)
    return [100.0, 200.0, 300.0, 400.0]


@app.post("/insert")
def insert(text: str):

    vector = fake_embedding(text)

    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"text": text}
            )
        ]
    )

    return {
        "status": "saved",
        "id": point_id,
        "vector": vector
    }




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)