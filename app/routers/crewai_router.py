from fastapi import APIRouter, HTTPException

from app.controllers.crewai_controller import run_crewai_agent
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/crewai", tags=["crewai"])


@router.post("/", response_model=ChatResponse)
async def crewai_chat(payload: ChatRequest) -> ChatResponse:
    """
    Endpoint para el agente multi-agente CrewAI.
    
    Este agente utiliza un sistema colaborativo de multiples agentes:
    
    1. **Agente Investigador**
       - Busca y recopila informacion sobre temas
       - Utiliza herramientas de busqueda
    
    2. **Agente Analista**
       - Analiza la informacion recopilada
       - Extrae conclusiones clave
       - Realiza calculos si es necesario
    
    3. **Agente Redactor**
       - Genera respuesta final coherente
       - Estructura la informacion
       - Asegura claridad y legibilidad
    
    Ejemplo:
        POST /crewai/
        {
            "input": "Que es Machine Learning?"
        }
        
        Respuesta:
        {
            "output": "Machine Learning es una rama de la IA que permite a las máquinas aprender sin ser programadas..."
        }
    """
    try:
        output = await run_crewai_agent(payload.input)
        return ChatResponse(output=output)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
