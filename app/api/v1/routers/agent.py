from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent import run_ai_agent_stream
from app.graph import graph
from app.models import schemas

router = APIRouter(
    tags=["Agent"]
)


@router.post("/ask-stream")
def ask_agent_stream(req: schemas.QueryRequest):

    return StreamingResponse(
        run_ai_agent_stream(req.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/ask")
def ask_agent(req: schemas.QueryRequest):

    result = graph.invoke({"question": req.question})

    return result