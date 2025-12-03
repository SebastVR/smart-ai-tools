from fastapi import APIRouter, HTTPException

from app.controllers.langgraph_controller import run_langgraph_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/langgraph", tags=["langgraph"])


@router.post("/", response_model=ChatResponse)
async def langgraph_chat(payload: ChatRequest) -> ChatResponse:
    """
    Endpoint para el agente LangGraph avanzado con tools y workflow.
    
    Este agente tiene capacidades adicionales:
    - Calculo matematico
    - Acceso a informacion
    - Traduccion de textos
    
    Example:
        POST /langgraph/
        {
            "input": "Calcula 2 + 2"
        }
    """
    try:
        output = await run_langgraph_agent(payload.input)
        return ChatResponse(output=output)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
