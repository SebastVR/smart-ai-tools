from app.agents.langgraph_agent import get_langgraph_agent

_agent = None


def _get_langgraph_agent():
    global _agent
    if _agent is None:
        _agent = get_langgraph_agent()
    return _agent


async def run_langgraph_agent(user_input: str) -> str:
    """
    Ejecuta el agente LangGraph avanzado con tools y workflow.
    
    Args:
        user_input: El mensaje del usuario
    
    Returns:
        La respuesta del agente
    """
    agent = _get_langgraph_agent()
    result = agent.invoke({"input": user_input})
    return result.get("output", str(result))
