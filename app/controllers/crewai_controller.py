from app.agents.crewai_agent import get_crewai_agent

_agent = None


def _get_crewai_agent():
    global _agent
    if _agent is None:
        _agent = get_crewai_agent()
    return _agent


async def run_crewai_agent(user_input: str) -> str:
    """
    Ejecuta el agente multi-agente CrewAI.
    
    Este agente utiliza multiples agentes especializados que colaboran:
    - Investigador: Busca informacion
    - Analista: Analiza la informacion
    - Redactor: Genera respuesta final
    
    Args:
        user_input: El mensaje del usuario
    
    Returns:
        La respuesta procesada por el crew
    """
    agent = _get_crewai_agent()
    result = agent.invoke({"input": user_input})
    return result.get("output", str(result))
