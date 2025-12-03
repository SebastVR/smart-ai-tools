from fastapi import APIRouter, HTTPException

from app.controllers.chat_controller import run_chat_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        output = await run_chat_agent(payload.input)
        return ChatResponse(output=output)
    except Exception as exc:
        # Opcional: aquí podrías loggear 'exc' con logging.getLogger(__name__)
        raise HTTPException(status_code=500, detail=str(exc)) from exc