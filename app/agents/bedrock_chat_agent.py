from __future__ import annotations

from typing import Any, Dict, Optional

import boto3
from botocore.config import Config
from langchain_core.language_models import BaseLLM
from langchain_core.messages import HumanMessage, AIMessage


def _get_bedrock_client() -> Any:
    """Crea cliente Bedrock Runtime usando credenciales fijas (hardcode)."""

    aws_access_key = ""
    aws_secret_key = ""
    aws_region = "us-east-1"

    if not aws_access_key or not aws_secret_key:
        raise RuntimeError("Missing hardcoded AWS credentials.")

    config = Config(retries={"max_attempts": 3, "mode": "standard"})

    return boto3.client(
        service_name="bedrock-runtime",
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        config=config,
    )


class BedrockLLMWrapper(BaseLLM):
    """Wrapper para usar Bedrock como LLM en LangChain."""
    
    model_id: str = "openai.gpt-oss-120b-1:0"
    client: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = _get_bedrock_client()
    
    def _generate(self, messages: list, **kwargs) -> str:
        """Genera una respuesta usando Bedrock."""
        # Convertir mensajes de LangChain a formato Bedrock
        bedrock_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                bedrock_messages.append({
                    "role": "user",
                    "content": [{"text": msg.content}],
                })
            elif isinstance(msg, AIMessage):
                bedrock_messages.append({
                    "role": "assistant",
                    "content": [{"text": msg.content}],
                })
        
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=bedrock_messages,
                inferenceConfig={
                    "maxTokens": 256,
                    "temperature": 0.1,
                },
            )
            
            # Extraer texto de la respuesta
            outputs = response.get("output", {}).get("message", {}).get("content", [])
            parts = []
            for block in outputs:
                text = block.get("text")
                if text:
                    parts.append(text)
            
            return "".join(parts) if parts else str(response)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "bedrock"


class BedrockChatAgent:
    """Agente LangChain basado en Bedrock."""
    
    def __init__(self):
        """Inicializa el agente con el LLM de Bedrock."""
        self.llm = BedrockLLMWrapper()
        print(f"[BedrockAgent] Using model: {self.llm.model_id}")
    
    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca el agente con un mensaje del usuario.
        
        Args:
            input_dict: Diccionario con la clave "input" conteniendo el mensaje del usuario
            
        Returns:
            Diccionario con la clave "output" conteniendo la respuesta del modelo
        """
        user_input = input_dict.get("input", "")
        
        if not user_input:
            return {"output": "Error: No input provided"}
        
        try:
            # Crear mensaje del usuario
            message = HumanMessage(content=user_input)
            
            # Invocar el LLM
            response_text = self.llm._generate([message])
            
            return {"output": response_text}
        except Exception as e:
            return {"output": f"Error: {str(e)}"}


def get_bedrock_llm_agent(tools: Optional[list] = None) -> BedrockChatAgent:
    """
    Crea un agente Bedrock basado en LangChain.
    
    Args:
        tools: Herramientas para el agente (puede extenderse en el futuro)
    
    Returns:
        BedrockChatAgent: Agente configurado
    
    Example:
        agent = get_bedrock_llm_agent()
        result = agent.invoke({"input": "Hola, como estás?"})
        print(result["output"])
    """
    return BedrockChatAgent()

