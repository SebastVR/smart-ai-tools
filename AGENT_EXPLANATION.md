# Explicación del Agente LangChain en Smart AI Tools

## 📍 Ubicación del Agente en el Proyecto

El agente está distribuido en varios archivos:

### 1. **Core del Agente** - `app/agents/bedrock_chat_agent.py`
Este es el archivo principal donde se define el agente.

#### Componentes principales:

```
bedrock_chat_agent.py
├── _get_bedrock_client()           # Cliente AWS Bedrock (conexión directa)
├── BedrockLLMWrapper(BaseLLM)      # Wrapper para integrar Bedrock en LangChain
├── BedrockChatAgent                # Clase que encapsula el agente
└── get_bedrock_llm_agent()         # Función que crea instancias del agente
```

---

## 🔄 Flujo de Ejecución Completo

### Paso 1: Usuario hace una petición HTTP
```
POST /chat/
{
  "input": "Hola, como estás?"
}
```

### Paso 2: Router recibe la petición
**Archivo:** `app/routers/chat_router.py`
```python
@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    output = await run_chat_agent(payload.input)
    return ChatResponse(output=output)
```
↓

### Paso 3: Controlador procesa el mensaje
**Archivo:** `app/controllers/chat_controller.py`
```python
async def run_chat_agent(user_input: str) -> str:
    agent = _get_agent()  # Obtiene la instancia cacheada del agente
    result = agent.invoke({"input": user_input})  # Invoca el agente
    return result.get("output", str(result))
```
↓

### Paso 4: Agente LangChain procesa el mensaje
**Archivo:** `app/agents/bedrock_chat_agent.py`

#### 4a. Crea instancia del agente
```python
def get_bedrock_llm_agent():
    return BedrockChatAgent()  # Inicializa con BedrockLLMWrapper
```

#### 4b. BedrockChatAgent.invoke() procesa el mensaje
```python
def invoke(self, input_dict):
    user_input = input_dict.get("input", "")
    # Crea un HumanMessage de LangChain
    message = HumanMessage(content=user_input)
    # Invoca el LLM
    response_text = self.llm._generate([message])
    return {"output": response_text}
```

#### 4c. BedrockLLMWrapper convierte y envía a Bedrock
```python
def _generate(self, messages: list) -> str:
    # Convierte mensajes LangChain → formato Bedrock
    bedrock_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            bedrock_messages.append({
                "role": "user",
                "content": [{"text": msg.content}]
            })
    
    # Llama a AWS Bedrock
    response = self.client.converse(
        modelId="openai.gpt-oss-120b-1:0",
        messages=bedrock_messages,
        inferenceConfig={"maxTokens": 256, "temperature": 0.1}
    )
    
    # Extrae el texto de la respuesta
    return extract_text(response)
```

### Paso 5: Respuesta regresa al usuario
```
{
  "output": "¡Hola! Estoy bien, gracias por preguntar..."
}
```

---

## 🏗️ Arquitectura del Agente

### Jerarquía de Clases

```
BaseLLM (de LangChain)
    ↓
BedrockLLMWrapper
    - Integra Bedrock como LLM de LangChain
    - Convierte mensajes LangChain → Bedrock
    - Implementa interfaz _llm_type y _generate
    ↓
BedrockChatAgent
    - Encapsula el BedrockLLMWrapper
    - Proporciona método invoke() compatible con el controlador
    - Maneja errores y formatea respuestas
```

---

## 🔌 Integración con LangChain

### ¿Por qué BedrockLLMWrapper hereda de BaseLLM?

`BaseLLM` es la clase base de LangChain para todos los modelos de lenguaje. Al heredar de ella:

1. **Compatibilidad** - Funciona con herramientas y componentes de LangChain
2. **Interfaz estándar** - Todos los LLMs de LangChain tienen la misma interfaz
3. **Conversión de mensajes** - LangChain maneja automáticamente `HumanMessage`, `AIMessage`, etc.
4. **Extensibilidad** - Fácil agregar herramientas (tools) en el futuro

### Métodos requeridos de BaseLLM

```python
class BedrockLLMWrapper(BaseLLM):
    
    @property
    def _llm_type(self) -> str:
        """Identificar el tipo de LLM"""
        return "bedrock"
    
    def _generate(self, messages: list, **kwargs) -> str:
        """Generar respuesta a partir de mensajes"""
        # Implementación aquí
        pass
```

---

## 📦 Flujo de Datos

```
Usuario
  ↓ (POST /chat/)
Router (chat_router.py)
  ↓ 
Controller (chat_controller.py)
  ↓ run_chat_agent()
Agent (bedrock_chat_agent.py)
  ├─ BedrockChatAgent.invoke()
  │   ├─ Crea HumanMessage
  │   └─ Llama a llm._generate()
  │       └─ BedrockLLMWrapper._generate()
  │           ├─ Convierte a formato Bedrock
  │           └─ Llama client.converse() (AWS Bedrock)
  │               └─ Obtiene respuesta
  │                   └─ Extrae texto
  └─ Retorna {"output": respuesta}
```

---

## 🔑 Características Principales

### 1. **Wrapper LLM de LangChain**
```python
# Permite usar Bedrock como cualquier LLM de LangChain
llm = BedrockLLMWrapper()
response = llm._generate([HumanMessage(content="Hola")])
```

### 2. **Conversión de Mensajes**
```
LangChain Format:          Bedrock Format:
HumanMessage          →    {"role": "user", "content": [...]}
AIMessage             →    {"role": "assistant", "content": [...]}
```

### 3. **Manejo de Errores**
```python
try:
    response = self.client.converse(...)
except Exception as e:
    return f"Error: {str(e)}"
```

### 4. **Caching de Instancias**
En el controlador:
```python
_agent = None

def _get_agent():
    global _agent
    if _agent is None:
        _agent = get_bedrock_llm_agent()  # Se crea una sola vez
    return _agent
```

---

## 🚀 Cómo Extender el Agente

### Opción 1: Agregar Herramientas (Tools)

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Obtiene el clima de una ciudad."""
    return f"Soleado en {city}"

# Pasar herramientas al agente
agent = get_bedrock_llm_agent(tools=[get_weather])
```

### Opción 2: Agregar Historial de Mensajes

```python
# Modificar BedrockChatAgent para mantener historial
class BedrockChatAgent:
    def __init__(self):
        self.llm = BedrockLLMWrapper()
        self.message_history = []  # Nuevo
    
    def invoke(self, input_dict):
        user_input = input_dict.get("input", "")
        
        # Agregar mensaje del usuario al historial
        self.message_history.append(HumanMessage(content=user_input))
        
        # Pasar historial completo al LLM
        response = self.llm._generate(self.message_history)
        
        # Agregar respuesta al historial
        self.message_history.append(AIMessage(content=response))
        
        return {"output": response}
```

### Opción 3: Usar LangGraph para Control de Flujo

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(AgentState)
graph.add_node("chat", process_message)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
agent = graph.compile()
```

---

## 📊 Resumen

| Componente | Propósito | Ubicación |
|---|---|---|
| **BaseLLM** | Base de LangChain para LLMs | langchain_core |
| **BedrockLLMWrapper** | Adapta Bedrock a interfaz LangChain | bedrock_chat_agent.py |
| **BedrockChatAgent** | Encapsula el agente para usar en controladores | bedrock_chat_agent.py |
| **get_bedrock_llm_agent()** | Factory function para crear agentes | bedrock_chat_agent.py |
| **Router** | Recibe peticiones HTTP | chat_router.py |
| **Controller** | Orquesta el flujo | chat_controller.py |
| **AWS Bedrock** | Servicio de LLM en la nube | AWS |

---

## ✅ Verificación

Para verificar que el agente está funcionando:

1. **Construye la imagen Docker**
```bash
docker build -t smart-ai-tools:latest .
```

2. **Ejecuta el contenedor**
```bash
docker run -p 8000:8000 smart-ai-tools:latest
```

3. **Prueba el endpoint**
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Hola"}'
```

4. **Respuesta esperada**
```json
{
  "output": "Respuesta del modelo Bedrock..."
}
```
