"""
Agente simple que conecta directamente a Bedrock usando solo boto3.
Sin LangChain, LangGraph ni CrewAI. Solo boto3 puro.
"""

import json
import boto3
from botocore.config import Config


def _get_bedrock_client():
    """Crea cliente Bedrock Runtime con credenciales fijas."""
    
    aws_access_key = ""
    aws_secret_key = ""
    aws_region = "us-east-1"
    
    config = Config(retries={"max_attempts": 3, "mode": "standard"})
    
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=aws_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        config=config,
    )


class BedrockSimpleAgent:
    """Agente simple que usa boto3 directamente sin frameworks."""
    
    def __init__(self):
        self.client = _get_bedrock_client()
        self.model_id = "openai.gpt-oss-120b-1:0"
        self.conversation_history = []
    
    def invoke(self, user_input: str) -> str:
        """
        Invoca el modelo de Bedrock directamente.
        
        Args:
            user_input: El mensaje del usuario
            
        Returns:
            La respuesta del modelo como string
        """
        # Agregar mensaje del usuario al historial
        self.conversation_history.append({
            "role": "user",
            "content": [{"text": user_input}]
        })
        
        # Llamar a Bedrock
        response = self.client.converse(
            modelId=self.model_id,
            messages=self.conversation_history,
            inferenceConfig={
                "maxTokens": 256,
                "temperature": 0.1
            }
        )
        
        # Extraer respuesta
        assistant_message = response["output"]["message"]["content"][0]["text"]
        
        # Agregar respuesta al historial
        self.conversation_history.append({
            "role": "assistant",
            "content": [{"text": assistant_message}]
        })
        
        return assistant_message
    
    def reset(self):
        """Limpia el historial de conversación."""
        self.conversation_history = []


# Instancia global del agente
_agent = None


def get_bedrock_simple_agent() -> BedrockSimpleAgent:
    """Factory function para obtener la instancia del agente."""
    global _agent
    if _agent is None:
        _agent = BedrockSimpleAgent()
    return _agent
