# 🚀 Smart AI Tools - Resumen del Proyecto

## ✅ Estado Final: COMPLETADO

Hemos construido un sistema completo con **4 agentes de IA** progresivamente complejos, todos conectados a **AWS Bedrock**, integrando tres frameworks diferentes: **LangChain**, **LangGraph** y **CrewAI**.

---

## 📊 Endpoints Disponibles

### 1️⃣ **POST `/simple/`** - Agente Simple (solo boto3)
**Stack**: boto3 puro

**Características**:
- Conexión directa a Bedrock sin frameworks
- Ideal para debugging y pruebas rápidas
- Mantiene historial de conversación

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/simple/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Hola, ¿qué es Python?"}'
```

**Respuesta**:
```json
{
  "output": "Python es un lenguaje de programación versátil..."
}
```

---

### 2️⃣ **POST `/chat/`** - Agente LangChain
**Stack**: LangChain + BedrockLLMWrapper + boto3

**Características**:
- Abstracción estándar de LangChain
- Conversación conversacional
- Interfaz consistente

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"input": "¿Cuál es la diferencia entre ML y IA?"}'
```

---

### 3️⃣ **POST `/langgraph/`** - Agente LangGraph (Avanzado)
**Stack**: LangGraph + State Management + Tools + boto3

**Características**:
- Flujo de trabajo con estado
- Herramientas integradas
- Lógica condicional

**Herramientas disponibles**:
- `calculate(expression)` - Calcula expresiones matemáticas
- `get_current_info(topic)` - Obtiene información general
- `translate_text(text, language)` - Traduce textos

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Calcula 2+2 y traduce el resultado al inglés"}'
```

---

### 4️⃣ **POST `/crewai/`** - Agente CrewAI (Multi-Agente Colaborativo)
**Stack**: CrewAI + 3 Agentes Especializados + 3 Herramientas

**Estructura**:

```
Tu Pregunta
    ↓
🔍 Agente Investigador
   └─ Busca información (search_information, analyze_text)
    ↓
📊 Agente Analista
   └─ Analiza resultados (analyze_text, calculate_math)
    ↓
✍️ Agente Redactor
   └─ Genera respuesta final (analyze_text)
    ↓
Respuesta Estructurada
```

**Herramientas**:
- `search_information(topic)` - Base de conocimiento local
- `analyze_text(text)` - Análisis de texto
- `calculate_math(expression)` - Cálculos matemáticos

**Preguntas que funcionan bien**:
```
"¿Qué es Machine Learning?"
"¿Por qué Python es importante para IA?"
"Calcula 150+250 y explícame el resultado"
"¿Cuáles son las aplicaciones del Deep Learning?"
```

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/crewai/ \
  -H "Content-Type: application/json" \
  -d '{"input": "¿Qué es la inteligencia artificial y cuáles son sus aplicaciones?"}'
```

---

## 🏗️ Arquitectura

### Estructura de Carpetas
```
smart-ai-tools/
├── app/
│   ├── agents/
│   │   ├── bedrock_simple_agent.py       # Agente simple (boto3)
│   │   ├── bedrock_chat_agent.py         # Agente LangChain
│   │   ├── langgraph_agent.py            # Agente LangGraph
│   │   └── crewai_agent.py               # Agente CrewAI
│   ├── controllers/
│   │   ├── simple_bedrock_controller.py
│   │   ├── chat_controller.py
│   │   ├── langgraph_controller.py
│   │   └── crewai_controller.py
│   ├── routers/
│   │   ├── simple_bedrock_router.py
│   │   ├── chat_router.py
│   │   ├── langgraph_router.py
│   │   └── crewai_router.py
│   ├── schemas/
│   │   └── chat.py                       # ChatRequest/ChatResponse
│   └── core/
│       ├── config.py
│       └── cors.py
├── main.py                                # FastAPI app entry point
├── requirements.txt                       # Python dependencies
├── Dockerfile                             # Container configuration
└── [Documentación]
    ├── AGENT_EXPLANATION.md
    ├── LANGGRAPH_AGENT_EXPLANATION.md
    └── CREWAI_EXPLANATION.md
```

### Stack Tecnológico
- **FastAPI 0.115.5** - Web framework
- **AWS Bedrock** - LLM provider
  - Model: `anthropic.claude-3-sonnet-20240229-v1:0` (CrewAI)
  - Model: `openai.gpt-oss-120b-1:0` (Simple, LangChain, LangGraph)
- **LangChain >= 0.2.11** - LLM abstraction
- **LangGraph >= 0.1.0** - Workflow orchestration
- **CrewAI >= 0.30.0** - Multi-agent framework
- **boto3 >= 1.34** - AWS SDK
- **Docker** - Containerization

---

## 🚀 Uso (Docker)

### Compilar imagen
```bash
docker build -t smart-ai-tools:latest .
```

### Ejecutar contenedor
```bash
docker run --rm -p 8000:8000 smart-ai-tools:latest
```

### Acceder a la API
```
http://localhost:8000/docs   # Swagger UI
http://localhost:8000/redoc  # ReDoc
```

---

## 🔐 Configuración de Credenciales

Las credenciales de AWS se configuran a través de variables de entorno:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
```

**Métodos soportados:**
1. Variables de entorno (recomendado)
2. AWS Credentials file (`~/.aws/credentials`)
3. AWS Secrets Manager
4. IAM Roles (en EC2 o ECS)

---

## 📈 Comparación de Agentes

| Aspecto | Simple | LangChain | LangGraph | CrewAI |
|---------|--------|-----------|-----------|--------|
| **Complejidad** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Herramientas** | ❌ | ❌ | ✅ | ✅ |
| **Workflow** | ❌ | ❌ | ✅ | ✅ |
| **Multi-Agentes** | ❌ | ❌ | ❌ | ✅ |
| **Mejor para** | Debug | Producción | Lógica compleja | Problemas complejos |

---

## 🧪 Testing de Endpoints

### Test 1: Simple
```bash
curl -X POST http://localhost:8000/simple/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Hola"}'
```

### Test 2: LangChain
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"input": "¿Qué es Python?"}'
```

### Test 3: LangGraph
```bash
curl -X POST http://localhost:8000/langgraph/ \
  -H "Content-Type: application/json" \
  -d '{"input": "Calcula 5+5"}'
```

### Test 4: CrewAI
```bash
curl -X POST http://localhost:8000/crewai/ \
  -H "Content-Type: application/json" \
  -d '{"input": "¿Qué es Machine Learning?"}'
```

---

## 📚 Documentación Adicional

- `AGENT_EXPLANATION.md` - Explicación detallada del agente LangChain
- `LANGGRAPH_AGENT_EXPLANATION.md` - Explicación del agente LangGraph
- `CREWAI_EXPLANATION.md` - Explicación del agente CrewAI
- `IMPORT_FIXES.md` - Registro de correcciones de importación

---

## 🎯 Próximos Pasos Potenciales

1. **Expandir Base de Conocimiento** - Agregar más temas a CrewAI
2. **APIs Externas** - Integrar búsqueda web real
3. **Persistencia** - Base de datos para historial de conversaciones
4. **Autenticación** - JWT o API keys
5. **Observabilidad** - Logging y tracing
6. **Performance** - Cache y optimización
7. **Escalabilidad** - Message queues, async processing

---

## ✨ Lecciones Aprendidas

1. ✅ **CrewLLM vs ChatBedrock**: CrewLLM es más directo para CrewAI
2. ✅ **Conversión de Mensajes**: Bedrock requiere formato específico
3. ✅ **Caching de LLM**: Importante para performance
4. ✅ **Herramientas Útiles**: Mejoran respuestas significativamente
5. ✅ **Multi-framework**: Cada uno tiene sus fortalezas

---

## 📞 Contacto / Support

Para preguntas o problemas:
1. Revisar documentación en `/AGENT_EXPLANATION.md`
2. Verificar logs del Docker
3. Revisar código fuente en `app/agents/`

---

**Proyecto completado el 2 de Diciembre de 2025** ✅

Todos los 4 agentes están funcionales y listos para producción.
