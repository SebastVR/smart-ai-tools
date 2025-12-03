"""
Router simple para el agente Bedrock puro (solo boto3).
"""

from fastapi import APIRouter
from app.controllers.simple_bedrock_controller import run_simple_bedrock_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/simple", tags=["simple"])


@router.post("/", response_model=ChatResponse)
async def simple_bedrock_chat(request: ChatRequest) -> ChatResponse:
    """
    Endpoint simple para chat directo con Bedrock usando solo boto3.
    
    Sin LangChain, sin LangGraph, sin CrewAI.
    Solo boto3 puro conectado directamente al modelo.
    
    Example:
        POST /simple/
        {
            "input": "¿Cuál es la capital de Francia?"
        }
        
        Response:
        {
            "output": "La capital de Francia es París."
        }
    """
    result = await run_simple_bedrock_agent(request.input)
    return ChatResponse(output=result["output"])
