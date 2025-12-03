from app.agents.bedrock_chat_agent import get_bedrock_llm_agent

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = get_bedrock_llm_agent()
    return _agent


async def run_chat_agent(user_input: str) -> str:
    agent = _get_agent()
    result = agent.invoke({"input": user_input})
    return result.get("output", str(result))