"""
Application entrypoint.

Exposes:
- /health -> simple health check
- Routers under /summarize (extractive and AI-based abstractive summarization)
"""

from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.routers.summarize_router import router as summarize_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Summarization API (extractive + AI) using only free, CPU-friendly models.",
)

# Configure permissive CORS for public consumption (tighten in production).
setup_cors(app)


@app.get("/health")
def health() -> dict:
    """Return a simple health payload."""
    return {"status": "ok"}


# Register API routers
app.include_router(summarize_router)