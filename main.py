from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from fastapi_swagger import patch_fastapi

from app.core import Base, app_engine
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> Running lifespan startup...")
    # Base.metadata.create_all(bind=app_engine)
    # print(">>> Database tables created!")
    yield
    print(">>> App shutting down...")


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    swagger_ui_oauth2_redirect_url=None,
)

patch_fastapi(app, docs_url="/swagger")

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)