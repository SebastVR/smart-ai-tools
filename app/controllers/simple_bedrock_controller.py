"""
Controlador simple para el agente Bedrock puro (solo boto3).
"""

from app.agents.bedrock_simple_agent import get_bedrock_simple_agent


async def run_simple_bedrock_agent(user_input: str) -> dict:
    """
    Ejecuta el agente simple de Bedrock.
    
    Args:
        user_input: El mensaje del usuario
        
    Returns:
        Dict con la estructura {"output": respuesta}
    """
    agent = get_bedrock_simple_agent()
    response = agent.invoke(user_input)
    
    return {"output": response}
