# Agente LangGraph Avanzado con Tools y Workflow

## 📍 Ubicación

```
app/agents/langgraph_agent.py          # Agente LangGraph con tools y workflow
app/controllers/langgraph_controller.py # Controlador del agente
app/routers/langgraph_router.py        # Router para el endpoint /langgraph
```

---

## 🎯 Características Principales

### 1. **Herramientas (Tools)**

El agente tiene 3 herramientas integradas:

```python
@tool
def calculate(expression: str) -> str:
    """Evalua una expresion matematica simple."""
    # Permite: "2+2", "10*5", etc.

@tool
def get_current_info(topic: str) -> str:
    """Obtiene informacion general sobre un tema."""
    # Base de datos: "tiempo", "date", "hora", "python", "langchain"

@tool
def translate_text(text: str, language: str) -> str:
    """Traduce un texto a otro idioma (simulado)."""
    # Soporta: "es", "en", "fr"
```

---

## 🔄 Workflow del Agente LangGraph

```
Usuario INPUT
    ↓
START
    ↓
[agent_node] 
    ├─ Recibe mensaje del usuario
    ├─ Invoca LLM con tools disponibles
    └─ LLM decide si necesita una herramienta
        ↓
        ├─ SI: Retorna tool_calls
        │   ↓
        │ [should_continue] → "tools"
        │   ↓
        │ [tool_node]
        │   ├─ Ejecuta herramienta
        │   └─ Retorna resultado
        │       ↓
        │     [agent_node] (nuevamente)
        │       └─ Procesa resultado
        │
        └─ NO: Retorna respuesta final
            ↓
          [should_continue] → "end"
            ↓
          END
    ↓
Usuario OUTPUT
```

---

## 🛠️ Componentes del Agente

### 1. **BedrockLLMWrapper**
```python
class BedrockLLMWrapper(BaseLLM):
    """LLM base para integrar Bedrock en LangChain"""
```
- Hereda de `BaseLLM`
- Convierte mensajes LangChain ↔ Bedrock
- Soporta `ToolMessage` para resultados de herramientas

### 2. **AgentState**
```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```
- Mantiene el historial de mensajes
- `add_messages` agrega mensajes al final del historial automáticamente

### 3. **Nodos del Grafo**

#### a) `agent_node`
```python
def agent_node(state: AgentState) -> dict:
    """Invoca el LLM con las herramientas disponibles"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": response}
```

#### b) `should_continue`
```python
def should_continue(state: AgentState) -> str:
    """Determina si ejecutar herramientas o terminar"""
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"  # Ejecutar herramientas
    else:
        return "end"    # Terminar
```

#### c) `tool_node`
```python
tool_node = ToolNode(tools)
```
- Ejecuta las herramientas solicitadas por el LLM
- Retorna `ToolMessage` con los resultados

### 4. **Conexiones del Grafo**
```python
graph_builder.add_edge(START, "agent")

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)

graph_builder.add_edge("tools", "agent")  # Loop para procesar resultados
```

---

## 📊 Flujo de Ejecución Paso a Paso

### Ejemplo: "Calcula 2 + 2"

```
1. Usuario: "Calcula 2 + 2"
   ↓
2. [agent_node]
   - Mensaje: HumanMessage("Calcula 2 + 2")
   - LLM analiza el mensaje
   - LLM decide usar la herramienta "calculate"
   - Retorna: AIMessage(tool_calls=[{"name": "calculate", "args": {"expression": "2+2"}}])
   ↓
3. [should_continue]
   - Detecta tool_calls
   - Retorna: "tools"
   ↓
4. [tool_node]
   - Ejecuta: calculate("2+2")
   - Resultado: "Resultado: 4"
   - Retorna: ToolMessage("Resultado: 4", tool_call_id="...")
   ↓
5. [agent_node] (nuevamente)
   - Recibe el ToolMessage con el resultado
   - LLM procesa: "El usuario pidió calcular, el resultado es 4"
   - Retorna: AIMessage("El resultado de 2 + 2 es 4")
   ↓
6. [should_continue]
   - Sin tool_calls
   - Retorna: "end"
   ↓
7. Usuario recibe: "El resultado de 2 + 2 es 4"
```

---

## 🔗 Integración con FastAPI

### Endpoint
```
POST /langgraph/
Content-Type: application/json

{
  "input": "Calcula 2 + 2"
}
```

### Flujo HTTP
```
FastAPI Router (/langgraph)
    ↓
langgraph_controller.run_langgraph_agent()
    ↓
LangGraphChatAgent.invoke()
    ↓
create_langgraph_agent().invoke({"messages": [HumanMessage(...)]})
    ↓
LangGraph Workflow
    ├─ agent_node
    ├─ should_continue
    ├─ tool_node (si aplica)
    └─ agent_node (si aplica)
    ↓
Respuesta final
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Cálculo Matemático
```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Calcula 25 * 4"}'
```

**Respuesta:**
```json
{
  "output": "El resultado de 25 * 4 es 100"
}
```

### Ejemplo 2: Obtener Información
```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Que es Python?"}'
```

**Respuesta:**
```json
{
  "output": "Python es un lenguaje de programacion interpretado"
}
```

### Ejemplo 3: Traducción
```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Traduce 'hello' al español"}'
```

**Respuesta:**
```json
{
  "output": "La traduccion es: hola"
}
```

---

## 🔧 Cómo Agregar Nuevas Herramientas

### Paso 1: Crear la Herramienta

```python
@tool
def get_weather(city: str) -> str:
    """Obtiene el clima de una ciudad.
    
    Args:
        city: El nombre de la ciudad
    
    Returns:
        El clima de la ciudad
    """
    # Implementacion
    return f"Clima en {city}: Soleado"
```

### Paso 2: Agregarla al Agente

```python
def create_langgraph_agent(tools: Optional[list] = None) -> Any:
    if tools is None:
        tools = [
            calculate,
            get_current_info,
            translate_text,
            get_weather,  # Nueva herramienta
        ]
    # ... resto del codigo
```

### Paso 3: Usar la Herramienta

```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Cual es el clima en Madrid?"}'
```

---

## 🎛️ Diferencias entre Agentes

| Característica | `/chat` (Simple) | `/langgraph` (Avanzado) |
|---|---|---|
| Framework | LangChain BaseLLM | LangGraph StateGraph |
| Herramientas | No | Sí (Tools) |
| Workflow | Directo | Con condicionales y loops |
| Historial | No persiste | Sí, en AgentState |
| Llamadas a LLM | 1 | Múltiples (si usa tools) |
| Complejidad | Baja | Media-Alta |
| Extensibilidad | Baja | Alta |

---

## 📋 Resumen

El **agente LangGraph avanzado** es un workflow inteligente que:

1. ✅ Recibe un mensaje del usuario
2. ✅ Analiza si necesita usar herramientas
3. ✅ Ejecuta las herramientas necesarias
4. ✅ Procesa los resultados
5. ✅ Genera una respuesta final

Todo dentro de un grafo que define claramente el flujo de control y permite agregar nodos y condicionales fácilmente.

---

## 🚀 Próximos Pasos

1. **Agregar más herramientas** - Database queries, API calls, etc.
2. **Persistencia de estado** - Guardar conversations en base de datos
3. **Control de loops** - Limitar iteraciones para evitar bucles infinitos
4. **Análisis de sentimiento** - Detectar emoción del usuario
5. **Integración con agentes externos** - Orquestar múltiples agentes
