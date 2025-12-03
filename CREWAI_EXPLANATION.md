# Agente Multi-Agente Colaborativo con CrewAI

## 📍 Ubicación

```
app/agents/crewai_agent.py          # Agente CrewAI multi-agente
app/controllers/crewai_controller.py # Controlador del agente
app/routers/crewai_router.py        # Router para el endpoint /crewai
```

---

## 🎯 ¿Qué es CrewAI?

CrewAI es un framework para construir **sistemas colaborativos de agentes de IA** donde múltiples agentes especializados trabajan juntos para completar tareas complejas.

### Diferencia clave:
- **LangChain**: Un solo agente inteligente
- **LangGraph**: Un agente con workflow y herramientas
- **CrewAI**: **Múltiples agentes colaborativos** cumpliendo tareas especializadas

---

## 👥 Los 3 Agentes del Crew

### 1. **Agente Investigador**
```python
role="Investigador"
goal="Buscar y compilar informacion precisa sobre temas solicitados"
tools=[search_information, analyze_text]
```
- Busca información sobre el tema
- Utiliza herramientas de búsqueda
- Recopila datos relevantes

### 2. **Agente Analista**
```python
role="Analista"
goal="Analizar y sintetizar informacion compleja en conclusiones claras"
tools=[analyze_text, calculate_math]
```
- Analiza la información recopilada
- Extrae conclusiones importantes
- Realiza cálculos si es necesario

### 3. **Agente Redactor**
```python
role="Redactor"
goal="Crear respuestas claras, concisas y bien estructuradas"
tools=[analyze_text]
```
- Redacta la respuesta final
- Estructura la información
- Asegura claridad y legibilidad

---

## 🔄 Flujo de Ejecución del Crew

```
Usuario INPUT: "Que es Machine Learning?"
    ↓
Crew.kickoff()
    ├─ [Tarea 1 - Investigador]
    │   ├─ Busca información sobre Machine Learning
    │   ├─ Utiliza search_information()
    │   └─ Resultado: "Machine Learning es una rama de la IA..."
    │       ↓
    ├─ [Tarea 2 - Analista]
    │   ├─ Recibe resultado del Investigador
    │   ├─ Analiza la información
    │   ├─ Extrae conclusiones clave
    │   └─ Resultado: "Análisis: ML es fundamental en IA moderna"
    │       ↓
    └─ [Tarea 3 - Redactor]
        ├─ Recibe análisis del Analista
        ├─ Redacta respuesta final
        ├─ Estructura y mejora la claridad
        └─ Resultado: "Respuesta final bien estructurada"
            ↓
Usuario OUTPUT: Respuesta completa y bien estructurada
```

---

## 🛠️ Componentes Clave

### 1. **Agent**
```python
Agent(
    role="Investigador",
    goal="Buscar y compilar informacion precisa",
    backstory="Eres un investigador experto...",
    tools=[search_information, analyze_text],
    verbose=True,
)
```
- Define el rol del agente
- Establece su objetivo
- Asigna herramientas disponibles
- Proporciona contexto (backstory)

### 2. **Task**
```python
Task(
    description="Investiga y recopila informacion sobre: {user_input}",
    agent=research_agent,
    expected_output="Informacion detallada y bien organizada",
)
```
- Define qué debe hacer un agente
- Especifica agente responsable
- Define output esperado

### 3. **Crew**
```python
Crew(
    agents=[research_agent, analyst_agent, writer_agent],
    tasks=[research_task, analysis_task, writing_task],
    verbose=True,
)
result = crew.kickoff()
```
- Orquesta múltiples agentes
- Ejecuta tareas secuencialmente
- Retorna resultado final

### 4. **Herramientas**
```python
@tool
def search_information(topic: str) -> str:
    """Busca informacion sobre un tema."""
    # Implementacion
```
- Funciones disponibles para los agentes
- Decoradas con `@tool`
- Con descripción y documentación clara

---

## 📊 Herramientas Disponibles

| Herramienta | Descripción | Usado por |
|---|---|---|
| `search_information` | Busca en base de conocimiento | Investigador |
| `analyze_text` | Analiza y resume texto | Analista, Redactor |
| `calculate_math` | Realiza cálculos | Analista |

---

## 🌐 Endpoint

```bash
# Agente CrewAI Multi-Agente
POST /crewai/
Content-Type: application/json

{
  "input": "Que es Python?"
}
```

### Respuesta:
```json
{
  "output": "Python es un lenguaje de programacion versátil, interpretado y de alto nivel. Conclusión: Es ideal para IA y Data Science"
}
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Preguntas Informativas
```bash
curl -X POST http://localhost:8000/crewai/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Que es IA?"}'
```

**Flujo:**
1. Investigador: Busca definición de IA
2. Analista: Analiza importancia y aplicaciones
3. Redactor: Genera respuesta coherente

### Ejemplo 2: Problemas Matemáticos
```bash
curl -X POST http://localhost:8000/crewai/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Calcula el promedio de 10, 20, 30"}'
```

**Flujo:**
1. Investigador: Busca método para promedios
2. Analista: Calcula el resultado (20)
3. Redactor: Explica el proceso

### Ejemplo 3: Análisis Complejos
```bash
curl -X POST http://localhost:8000/crewai/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Explica como funciona Machine Learning"}'
```

**Flujo:**
1. Investigador: Busca información detallada
2. Analista: Extrae conceptos clave
3. Redactor: Estructura explicación clara

---

## 🔧 Cómo Agregar Nuevos Agentes

### Paso 1: Crear el Agente
```python
def create_specialist_agent() -> Agent:
    """Agente especializado en tareas específicas."""
    return Agent(
        role="Especialista",
        goal="Especializar en un dominio específico",
        backstory="Eres un experto en tu dominio...",
        tools=[tu_herramienta],
        verbose=True,
    )
```

### Paso 2: Agregar Tarea para el Agente
```python
specialist_task = Task(
    description="Realiza tarea especializada sobre: {user_input}",
    agent=specialist_agent,
    expected_output="Resultado especializado",
)
```

### Paso 3: Agregar al Crew
```python
crew = Crew(
    agents=[research_agent, analyst_agent, writer_agent, specialist_agent],
    tasks=[research_task, analysis_task, writing_task, specialist_task],
)
```

---

## 🔧 Cómo Agregar Nuevas Herramientas

### Paso 1: Crear la Herramienta
```python
@tool
def new_tool(param: str) -> str:
    """Descripcion clara de la herramienta.
    
    Args:
        param: Descripcion del parametro
    
    Returns:
        Descripcion del resultado
    """
    # Implementacion
    return resultado
```

### Paso 2: Asignar a Agentes
```python
agent = Agent(
    role="...",
    goal="...",
    tools=[existing_tool, new_tool],  # Agregar nueva herramienta
)
```

---

## 📊 Comparación de Agentes

| Característica | `/chat` | `/langgraph` | `/crewai` |
|---|---|---|---|
| **Framework** | LangChain | LangGraph | CrewAI |
| **Agentes** | 1 | 1 | Múltiples |
| **Herramientas** | No | Sí | Sí |
| **Workflow** | Directo | Condicional | Secuencial |
| **Colaboración** | No | No | Sí |
| **Especialización** | General | General | Especializada |
| **Complejidad** | Baja | Media | Media-Alta |
| **Casos de uso** | Chat simple | Tareas con tools | Proyectos complejos |

---

## ✅ Ventajas de CrewAI

1. **Agentes Especializados** - Cada agente tiene un rol claro
2. **Colaboración** - Los agentes trabajan juntos hacia un objetivo
3. **Escalable** - Fácil agregar nuevos agentes y tareas
4. **Flexible** - Herramientas customizables por agente
5. **Estructurado** - Flujo claro y predecible
6. **Producción Ready** - Diseñado para aplicaciones en producción

---

## 🚀 Próximos Pasos

1. **Agregar más herramientas** - API calls, database queries, etc.
2. **Persistencia de conversaciones** - Guardar conversaciones
3. **Agentes con memoria** - Recordar contexto previo
4. **Procesamiento paralelo** - Ejecutar tareas en paralelo
5. **Integraciones externas** - Slack, Gmail, APIs, etc.
6. **Logging y monitoreo** - Rastrear ejecución del crew

---

## 📌 Resumen

**CrewAI** es la solución perfecta cuando necesitas:
- ✅ Múltiples agentes colaborativos
- ✅ Roles y responsabilidades claras
- ✅ Herramientas especializadas por agente
- ✅ Workflows estructurados y complejos
- ✅ Aplicaciones production-ready

Ahora tienes **3 tipos de agentes**:
- `/chat` - Simple y directo
- `/langgraph` - Avanzado con tools y workflow
- `/crewai` - Multi-agente colaborativo
