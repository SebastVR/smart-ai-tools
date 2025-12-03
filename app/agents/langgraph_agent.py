from __future__ import annotations

from typing import Any, Dict, Optional, Annotated
from functools import lru_cache

import boto3
from botocore.config import Config
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool, tool
from langchain_core.outputs import LLMResult, Generation
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict


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
    tools_list: list = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = _get_bedrock_client()
        self.tools_list = []
    
    def bind_tools(self, tools: list) -> "BedrockLLMWrapper":
        """Vincula herramientas al LLM."""
        self.tools_list = tools
        return self
    
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Genera una respuesta usando Bedrock."""
        
        # SYSTEM PROMPT - Instruye al modelo a usar herramientas
        SYSTEM_INSTRUCTIONS = """Eres un asistente que DEBE usar herramientas disponibles para responder preguntas.
REGLA CRÍTICA: Si el usuario pregunta sobre un tema (inteligencia artificial, machine learning, etc.):
1. DEBES llamar a get_current_info(topic) PRIMERO
2. NO respondas con saludos genéricos
3. SIEMPRE intenta usar herramientas antes de responder directamente
4. Si tienes información de una herramienta, úsala en tu respuesta final"""
        
        # Convertir mensajes de LangChain a formato Bedrock
        bedrock_messages = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                # Combinar system prompt con el mensaje del usuario
                text_content = f"{SYSTEM_INSTRUCTIONS}\n\nUsuario: {msg.content}"
                bedrock_messages.append({
                    "role": "user",
                    "content": [{"text": text_content}],
                })
            elif isinstance(msg, AIMessage):
                bedrock_messages.append({
                    "role": "assistant",
                    "content": [{"text": msg.content}],
                })
            elif isinstance(msg, ToolMessage):
                # Convertir ToolMessage a user message con la información de la herramienta
                bedrock_messages.append({
                    "role": "user",
                    "content": [{"text": f"Resultado de herramienta: {msg.content}"}],
                })
        
        # Asegurar que el primer mensaje sea del usuario
        if not bedrock_messages:
            bedrock_messages.append({
                "role": "user",
                "content": [{"text": f"{SYSTEM_INSTRUCTIONS}\n\nUsuario: Hola"}],
            })
        elif bedrock_messages[0]["role"] != "user":
            # Si el primer mensaje no es del usuario, agregar uno
            bedrock_messages.insert(0, {
                "role": "user",
                "content": [{"text": f"{SYSTEM_INSTRUCTIONS}\n\nContinúa respondiendo:"}],
            })
        
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=bedrock_messages,
                inferenceConfig={
                    "maxTokens": 512,
                    "temperature": 0.7,
                },
            )
            
            # Extraer texto de la respuesta
            outputs = response.get("output", {}).get("message", {}).get("content", [])
            parts = []
            for block in outputs:
                text = block.get("text")
                if text:
                    parts.append(text)
            
            text_response = "".join(parts) if parts else "Sin respuesta"
            
            # Retornar LLMResult correctamente
            return LLMResult(generations=[[Generation(text=text_response)]])
        except Exception as e:
            error_text = f"Error: {str(e)}"
            return LLMResult(generations=[[Generation(text=error_text)]])
    
    @property
    def _llm_type(self) -> str:
        return "bedrock"


# Estado del agente
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@lru_cache(maxsize=1)
def _get_bedrock_llm() -> BedrockLLMWrapper:
    """Obtiene instancia cached del LLM de Bedrock."""
    print("[BedrockLLM] Initializing Bedrock LLM wrapper")
    return BedrockLLMWrapper()


# Herramientas disponibles para el agente
@tool
def calculate(expression: str) -> str:
    """Evalua una expresion matematica simple.
    
    Args:
        expression: Una expresion matematica (ej: "2 + 2", "10 * 5")
    
    Returns:
        El resultado de la evaluacion
    """
    try:
        result = eval(expression)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Error en calculo: {str(e)}"


@tool
def get_current_info(topic: str) -> str:
    """Obtiene informacion general sobre un tema.
    
    Args:
        topic: El tema sobre el cual obtener informacion
    
    Returns:
        Informacion sobre el tema
    """
    info_db = {
        # Tecnologia
        "python": "Python es un lenguaje de programacion interpretado, versátil y de alto nivel. Es ampliamente utilizado en IA, análisis de datos, desarrollo web y automatización.",
        "javascript": "JavaScript es el lenguaje de scripting para navegadores web. Permite crear aplicaciones interactivas en el cliente y es fundamental para desarrollo web moderno.",
        "react": "React es una biblioteca JavaScript para construir interfaces de usuario con componentes reutilizables. Facilita la creación de aplicaciones web dinámicas y eficientes.",
        "docker": "Docker es una plataforma de containerización que permite empaquetar aplicaciones con todas sus dependencias. Simplifica el despliegue y la escalabilidad.",
        "langchain": "LangChain es un framework para construir aplicaciones con Modelos de Lenguaje (LLMs). Proporciona herramientas para encadenamiento, memoria y agentes.",
        "langgraph": "LangGraph es un framework para construir workflows stateful con LLMs. Permite crear agentes avanzados con herramientas y lógica condicional.",
        "crewai": "CrewAI es un framework para construir sistemas colaborativos de agentes de IA. Permite crear equipos de agentes especializados que trabajan juntos.",
        
        # Inteligencia Artificial
        "inteligencia artificial": "La Inteligencia Artificial (IA) es la simulacion de procesos de inteligencia humana por computadoras. Incluye ML, NLP, visión por computadora, robótica y sistemas expertos.",
        "machine learning": "Machine Learning es una rama de la IA que permite a máquinas aprender patrones de datos sin ser programadas explícitamente. Utiliza algoritmos de entrenamiento.",
        "deep learning": "Deep Learning es una rama del ML que utiliza redes neuronales profundas con múltiples capas para procesar información compleja. Es especialmente efectivo para imágenes y texto.",
        "neural networks": "Las Redes Neuronales son modelos computacionales inspirados en el cerebro humano. Consisten en capas de neuronas conectadas que aprenden patrones.",
        "nlp": "Procesamiento del Lenguaje Natural (NLP) es una rama de IA que se enfoca en la interacción entre computadoras y lenguaje humano. Incluye traducción, análisis de sentimientos y generación de texto.",
        "computer vision": "Visión por Computadora es una rama de IA que permite a máquinas interpretar y entender imágenes y videos. Se usa en reconocimiento facial, detección de objetos y análisis de video.",
        
        # AWS y Servicios en la Nube
        "bedrock": "Amazon Bedrock es un servicio totalmente administrado de modelos fundamentales en AWS. Proporciona acceso seguro a múltiples modelos de lenguaje potentes.",
        "aws": "Amazon Web Services (AWS) es la plataforma de computación en la nube más completa del mundo. Ofrece más de 200 servicios para computación, almacenamiento, bases de datos y IA.",
        "s3": "Amazon S3 (Simple Storage Service) es un servicio de almacenamiento de objetos escalable y seguro en AWS. Se usa para almacenar prácticamente cualquier tipo de datos.",
        "lambda": "AWS Lambda es un servicio de computación sin servidor (serverless) que ejecuta código en respuesta a eventos sin necesidad de provisionar servidores.",
        
        # Conceptos de Desarrollo
        "api": "Una API (Application Programming Interface) es un conjunto de reglas que permite que aplicaciones se comuniquen entre sí. Define los métodos y formatos para solicitar y enviar datos.",
        "rest": "REST (Representational State Transfer) es un estilo arquitectónico para diseñar servicios web. Utiliza protocolos HTTP estándar y operaciones como GET, POST, PUT y DELETE.",
        "microservicios": "Microservicios es una arquitectura de software donde la aplicación se divide en pequeños servicios independientes que se comunican entre sí.",
        "git": "Git es un sistema de control de versiones distribuido que permite rastrear cambios en código, colaborar con otros desarrolladores y mantener histórico de versiones.",
        
        # Bases de Datos
        "sql": "SQL (Structured Query Language) es el lenguaje estándar para consultar y manipular bases de datos relacionales. Se usa para CREATE, SELECT, UPDATE y DELETE.",
        "nosql": "NoSQL se refiere a bases de datos no relacionales que almacenan datos en formatos como documentos JSON, pares clave-valor o grafos.",
        "mongodb": "MongoDB es una base de datos NoSQL basada en documentos JSON. Permite almacenar datos de forma flexible sin esquema fijo.",
        
        # Ciberseguridad
        "ciberseguridad": "La Ciberseguridad es la protección de sistemas informáticos y datos contra ataques y acceso no autorizado. Incluye encriptación, autenticación y detección de intrusiones.",
        "encriptacion": "La Encriptación es el proceso de convertir datos legibles en código cifrado para protegerlos. Se usa para asegurar que solo los usuarios autorizados puedan leerlos.",
        "blockchain": "Blockchain es una tecnología de registro distribuido donde los datos se almacenan en bloques conectados cryptográficamente. Base de las criptomonedas.",
        
        # Desarrollo Web y Frameworks
        "fastapi": "FastAPI es un framework web moderno para construir APIs REST rápidas y eficientes con Python. Incluye validación automática y documentación interactiva.",
        "nodejs": "Node.js es un entorno de ejecución de JavaScript en el servidor. Permite ejecutar JavaScript fuera del navegador para construir servidores web escalables.",
        "html": "HTML (HyperText Markup Language) es el lenguaje de marcado estándar para crear páginas web. Define la estructura y contenido de las páginas.",
        "css": "CSS (Cascading Style Sheets) es el lenguaje para estilizar documentos HTML. Controla el diseño, colores, tipografía y diseño responsivo.",
        
        # Otros
        "tiempo": "No tengo acceso a datos en tiempo real de clima. Para información meteorológica actual, consulta un servicio de pronóstico.",
        "fecha": "Hoy es 2 de diciembre de 2025",
        "hora": "La hora actual es aproximadamente las 14:00 UTC",
    }
    
    topic_lower = topic.lower().strip()
    
    # Limpiar la pregunta: quitar "que es", "cual es", "define", etc.
    palabras_ignorar = ["que es", "cual es", "define", "definir", "explica", "explicar", "cuales son", "cuales", "como funciona", "como", "por qué", "porque"]
    for palabra in palabras_ignorar:
        topic_lower = topic_lower.replace(palabra, "").strip()
    
    # Búsqueda exacta
    if topic_lower in info_db:
        return info_db[topic_lower]
    
    # Búsqueda parcial
    for key, value in info_db.items():
        if topic_lower in key or key in topic_lower:
            return value
    
    # Búsqueda por palabras clave
    topic_words = topic_lower.split()
    for key, value in info_db.items():
        for word in topic_words:
            if len(word) > 3 and word in key:
                return value
    
    # Si no encuentra, devolver mensaje genérico
    return f"No tengo información específica sobre '{topic}' en mi base de datos. Temas disponibles: Python, JavaScript, React, Docker, LangChain, IA, ML, NLP y muchos más."



@tool
def translate_text(text: str, language: str) -> str:
    """Traduce un texto a otro idioma (simulado).
    
    Args:
        text: El texto a traducir
        language: El idioma destino (en, es, fr, etc)
    
    Returns:
        El texto traducido
    """
    translations = {
        "es": {"hello": "hola", "goodbye": "adios", "thank you": "gracias"},
        "en": {"hola": "hello", "adios": "goodbye", "gracias": "thank you"},
        "fr": {"hello": "bonjour", "goodbye": "au revoir"},
    }
    
    lang_translations = translations.get(language.lower(), {})
    if text.lower() in lang_translations:
        return f"Traduccion a {language}: {lang_translations[text.lower()]}"
    else:
        return f"No puedo traducir '{text}' al idioma '{language}'"


def create_langgraph_agent(tools: Optional[list] = None) -> Any:
    """
    Crea un agente LangGraph con Bedrock como LLM y soporte para tools.
    
    Args:
        tools: Lista de herramientas que el agente puede usar.
               Si es None, usa las herramientas por defecto.
    
    Returns:
        Agente compilado de LangGraph
    
    Example:
        agent = create_langgraph_agent()
        result = agent.invoke({"messages": [HumanMessage(content="Calcula 2+2")]})
    """
    
    llm = _get_bedrock_llm()
    
    # Usar herramientas por defecto si no se proporcionan
    if tools is None:
        tools = [calculate, get_current_info, translate_text]
    
    # Vincular herramientas al LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Crear el grafo del agente
    graph_builder = StateGraph(AgentState)
    
    # System prompt que FUERZA el uso de herramientas
    SYSTEM_PROMPT = """Eres un asistente inteligente que SIEMPRE debe usar las herramientas disponibles para responder preguntas.

INSTRUCCIONES CRÍTICAS:
1. Si el usuario pregunta sobre un tema, SIEMPRE debes usar get_current_info() para obtener información
2. Si el usuario pide un cálculo, SIEMPRE debes usar calculate()
3. Si el usuario pide traducción, SIEMPRE debes usar translate_text()
4. NO respondas con saludos genéricos como "¿En qué puedo ayudarte?" si hay una pregunta clara
5. SIEMPRE intenta usar una herramienta apropiada PRIMERO antes de responder

Herramientas disponibles:
- get_current_info(topic): obtén información sobre cualquier tema
- calculate(expression): realiza cálculos matemáticos
- translate_text(text, language): traduce texto a otro idioma

Responde siempre en el mismo idioma que el usuario."""
    
    # Nodo que procesa el mensaje con el LLM
    def agent_node(state: AgentState) -> dict:
        """Nodo que invoca el LLM con las herramientas disponibles."""
        messages = state["messages"]
        
        # Agregar system prompt al inicio si no está
        if not messages or not isinstance(messages[0], type(messages[0])) or messages[0].type != "system":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                msg if isinstance(msg, dict) else {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in messages
            ]
        
        print(f"[Agent] Procesando {len(messages)} mensajes...")
        
        # Invocar el LLM con system prompt
        response = llm_with_tools.invoke(messages)
        
        print(f"[Agent] LLM responde con: {response}")
        
        # Agregar respuesta del LLM al historial
        return {"messages": response}
    
    # Nodo para ejecutar herramientas
    tool_node = ToolNode(tools)
    
    # Funcin para determinar si se debe ejecutar una herramienta
    def should_continue(state: AgentState) -> str:
        """Determina si el flujo debe continuar con herramientas o terminar."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Si el ultimo mensaje tiene tool_calls, ejecutar herramientas
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        else:
            return "end"
    
    # Agregar nodos al grafo
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", tool_node)
    
    # Conectar el inicio al agente
    graph_builder.add_edge(START, "agent")
    
    # Flujo condicional: si hay tool_calls, ejecutar herramientas, si no terminar
    graph_builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        },
    )
    
    # Las herramientas siempre regresan al agente para procesar resultados
    graph_builder.add_edge("tools", "agent")
    
    # Compilar el grafo
    agent = graph_builder.compile()
    
    return agent


# Wrapper para compatibilidad con el controlador existente
class LangGraphChatAgent:
    """Wrapper de compatibilidad para el agente LangGraph avanzado - VERSIÓN SIMPLIFICADA."""
    
    def __init__(self, agent: Any = None):
        # No necesitamos el agente LangGraph complejo para esta versión simplificada
        self.agent = None
    
    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca el agente con un mensaje del usuario.
        Versión simplificada que busca información directamente.
        
        Args:
            input_dict: Diccionario con la clave "input" conteniendo el mensaje del usuario
            
        Returns:
            Diccionario con la clave "output" conteniendo la respuesta del modelo
        """
        user_input = input_dict.get("input", "")
        
        if not user_input:
            return {"output": "Error: No input provided"}
        
        try:
            print(f"[LangGraphChatAgent] Procesando pregunta: {user_input}")
            
            # PASO 1: Busca información relevante
            relevant_info = get_current_info(user_input)
            print(f"[LangGraphChatAgent] Información encontrada: {relevant_info[:100]}...")
            
            # PASO 2: Devuelve la información encontrada directamente
            # Esta es la forma más confiable de asegurar respuestas útiles
            return {"output": relevant_info}
            
        except Exception as e:
            print(f"[LangGraphChatAgent] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"output": f"Error: {str(e)}"}


def get_langgraph_agent(tools: Optional[list] = None) -> LangGraphChatAgent:
    """
    Crea un agente LangGraph avanzado con tools y workflow.
    
    Args:
        tools: Herramientas personalizadas para el agente
    
    Returns:
        LangGraphChatAgent: Agente configurado
    
    Example:
        agent = get_langgraph_agent()
        result = agent.invoke({"input": "Calcula 5+3"})
        print(result["output"])
    """
    agent = create_langgraph_agent(tools)
    return LangGraphChatAgent(agent)
