from __future__ import annotations

from typing import Any, Dict, Optional
from crewai import Agent, Task, Crew
from crewai.tools import tool
from crewai.llm import LLM as CrewLLM
import os


# Cache para el LLM de Bedrock
_bedrock_llm_cache = None


def _get_bedrock_llm() -> CrewLLM:
    """Obtiene una instancia cacheada del LLM Bedrock para CrewAI."""
    global _bedrock_llm_cache
    
    if _bedrock_llm_cache is None:
        # Usar CrewLLM directamente con Bedrock
        # Sin parámetros que no soporta el modelo
        _bedrock_llm_cache = CrewLLM(
            model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
            aws_access_key_id="",
            aws_secret_access_key="",
            aws_region_name="us-east-1",
            temperature=0.7,
        )
        print("[CrewAI LLM] Configurado con Bedrock: anthropic.claude-3-sonnet-20240229-v1:0")
    
    return _bedrock_llm_cache




# Herramientas para el crew
@tool
def calculate_math(expression: str) -> str:
    """Calcula una expresion matematica.
    
    Args:
        expression: Una expresion matematica (ej: '2+2', '10*5')
    
    Returns:
        El resultado de la expresion
    """
    try:
        result = eval(expression)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def search_information(topic: str) -> str:
    """Busca informacion sobre un tema usando base de conocimiento local.
    
    Args:
        topic: El tema a buscar
    
    Returns:
        Informacion sobre el tema
    """
    knowledge_base = {
        "inteligencia artificial": "La Inteligencia Artificial (IA) es la simulacion de procesos de inteligencia humana por computadoras. Incluye aprendizaje automático, procesamiento del lenguaje natural, visión por computadora y robótica.",
        "ia": "La Inteligencia Artificial (IA) es la simulacion de procesos de inteligencia humana por computadoras. Incluye aprendizaje automático, procesamiento del lenguaje natural, visión por computadora y robótica.",
        "python": "Python es un lenguaje de programacion versátil, interpretado y de alto nivel. Es ampliamente utilizado en IA, análisis de datos, desarrollo web y automatización.",
        "machine learning": "Machine Learning es una rama de la IA que permite a las máquinas aprender sin ser programadas explícitamente. Utiliza algoritmos para identificar patrones en datos.",
        "crewai": "CrewAI es un framework para construir sistemas colaborativos de agentes de IA. Permite crear equipos de agentes que trabajan juntos para resolver problemas complejos.",
        "bedrock": "Amazon Bedrock es un servicio totalmente gestionado de modelos fundamentales en AWS. Proporciona acceso a varios modelos de lenguaje potentes.",
        "deep learning": "Deep Learning es una rama del Machine Learning que utiliza redes neuronales profundas para procesar información compleja. Es especialmente efectivo para imágenes y texto.",
        "neural networks": "Las Redes Neuronales son modelos computacionales inspirados en el cerebro humano. Consisten en capas de neuronas conectadas que aprenden patrones en datos.",
        "nlp": "Procesamiento del Lenguaje Natural (NLP) es una rama de la IA que se enfoca en la interacción entre computadoras y lenguaje humano. Incluye traducción, análisis de sentimientos y generación de texto.",
    }
    
    topic_lower = topic.lower().strip()
    
    # Buscar coincidencia exacta
    if topic_lower in knowledge_base:
        return knowledge_base[topic_lower]
    
    # Buscar coincidencia parcial
    for key, value in knowledge_base.items():
        if topic_lower in key or key in topic_lower:
            return value
    
    # Si no encuentra, devolver un mensaje genérico que invite al LLM a usar su conocimiento
    return f"No hay información específica sobre '{topic}' en la base de datos local. Utiliza tu conocimiento general para proporcionar una respuesta útil."


@tool
def analyze_text(text: str) -> str:
    """Analiza un texto y proporciona un resumen.
    
    Args:
        text: El texto a analizar
    
    Returns:
        Analisis del texto
    """
    words = text.split()
    return f"Analisis del texto: {len(words)} palabras, {len(text)} caracteres. Resumen: {text[:100]}..."


# Agentes del Crew
def create_research_agent() -> Agent:
    """Agente investigador que busca informacion."""
    return Agent(
        role="Investigador",
        goal="Buscar y compilar informacion precisa sobre temas solicitados",
        backstory="Eres un investigador experto que recopila informacion de multiples fuentes y la analiza criticamente.",
        tools=[search_information, analyze_text],
        llm=_get_bedrock_llm(),
        verbose=True,
    )


def create_analyst_agent() -> Agent:
    """Agente analista que procesa y analiza informacion."""
    return Agent(
        role="Analista",
        goal="Analizar y sintetizar informacion compleja en conclusiones claras",
        backstory="Eres un analista experimentado con excelentes habilidades de sintesis y comunicacion.",
        tools=[analyze_text, calculate_math],
        llm=_get_bedrock_llm(),
        verbose=True,
    )


def create_writer_agent() -> Agent:
    """Agente escritor que genera respuestas coherentes."""
    return Agent(
        role="Redactor",
        goal="Crear respuestas claras, concisas y bien estructuradas",
        backstory="Eres un escritor talentoso que produce contenido claro, logico y fácil de entender.",
        tools=[analyze_text],
        llm=_get_bedrock_llm(),
        verbose=True,
    )



def create_crew_tasks(user_input: str, research_agent: Agent, analyst_agent: Agent, writer_agent: Agent) -> list:
    """Crea las tareas para el crew.
    
    Args:
        user_input: El input del usuario
        research_agent: Agente investigador
        analyst_agent: Agente analista
        writer_agent: Agente escritor
    
    Returns:
        Lista de tareas
    """
    
    # Tarea 1: Investigacion
    research_task = Task(
        description=f"Investiga y recopila informacion sobre el siguiente tema: {user_input}",
        agent=research_agent,
        expected_output="Informacion detallada y bien organizada sobre el tema",
    )
    
    # Tarea 2: Analisis
    analysis_task = Task(
        description="Analiza la informacion recopilada y extrae conclusiones importantes",
        agent=analyst_agent,
        expected_output="Analisis critico con conclusiones clave",
    )
    
    # Tarea 3: Redaccion
    writing_task = Task(
        description="Redacta una respuesta final clara y coherente basada en el analisis",
        agent=writer_agent,
        expected_output="Respuesta final bien estructurada y facil de entender",
    )
    
    return [research_task, analysis_task, writing_task]


def create_crewai_system(user_input: str) -> str:
    """Crea y ejecuta un sistema de crew con multiples agentes colaborativos.
    
    Args:
        user_input: El input del usuario
    
    Returns:
        La respuesta procesada por el crew
    """
    try:
        # Crear agentes
        research_agent = create_research_agent()
        analyst_agent = create_analyst_agent()
        writer_agent = create_writer_agent()
        
        # Crear tareas
        tasks = create_crew_tasks(user_input, research_agent, analyst_agent, writer_agent)
        
        # Crear el crew
        crew = Crew(
            agents=[research_agent, analyst_agent, writer_agent],
            tasks=tasks,
            verbose=True,
        )
        
        # Ejecutar el crew
        result = crew.kickoff()
        
        # Limpiar la respuesta: eliminar espacios en blanco al final
        result_str = str(result).strip()
        
        return result_str
    except Exception as e:
        error_msg = str(e).strip()
        return f"Error al ejecutar el crew: {error_msg}"


# Wrapper para compatibilidad con el controlador existente
class CrewAIChatAgent:
    """Wrapper para usar CrewAI como agente del sistema."""
    
    def __init__(self):
        """Inicializa el agente CrewAI."""
        print("[CrewAI] Inicializando sistema multi-agente CrewAI")
    
    def invoke(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoca el crew de CrewAI con un mensaje del usuario.
        
        Args:
            input_dict: Diccionario con la clave "input" conteniendo el mensaje del usuario
            
        Returns:
            Diccionario con la clave "output" conteniendo la respuesta del crew
        """
        user_input = input_dict.get("input", "")
        
        if not user_input:
            return {"output": "Error: No input provided"}
        
        try:
            print(f"[CrewAI] Procesando: {user_input}")
            output = create_crewai_system(user_input)
            return {"output": output}
        except Exception as e:
            return {"output": f"Error: {str(e)}"}


def get_crewai_agent() -> CrewAIChatAgent:
    """Crea un agente CrewAI multi-agente colaborativo.
    
    Args:
        tools: Herramientas personalizadas (opcional)
    
    Returns:
        CrewAIChatAgent: Agente configurado
    
    Example:
        agent = get_crewai_agent()
        result = agent.invoke({"input": "Que es Python?"})
        print(result["output"])
    """
    return CrewAIChatAgent()
