"""
Smart AI Tools - Main Application
- /health
- /summarize
- /summarize/ai (model loads lazily on first call)
- /simple (agente simple con solo boto3 puro)
- /chat (agente simple con LangChain)
- /langgraph (agente avanzado con LangGraph, tools y workflow)
- /crewai (agente multi-agente colaborativo con CrewAI)
"""

from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.routers.summarize_router import router as summarize_router
from app.routers.transcribe_router import router as transcribe_router
from app.routers.simple_bedrock_router import router as simple_bedrock_router
from app.routers.chat_router import router as chat_router
from app.routers.langgraph_router import router as langgraph_router
from app.routers.crewai_router import router as crewai_router
# NOTE: we do NOT import get_pipeline here to avoid side effects on startup.
# The controller/service will import and call it only when /summarize/ai is hit.

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Summarization API (extractive + AI) using free CPU-friendly models.",
)

setup_cors(app)

@app.get("/health")
def health() -> dict:
    """Simple health check."""
    return {"status": "ok"}

# Register routes last
app.include_router(summarize_router)
app.include_router(transcribe_router)
app.include_router(simple_bedrock_router)
app.include_router(chat_router)
app.include_router(langgraph_router)
app.include_router(crewai_router)