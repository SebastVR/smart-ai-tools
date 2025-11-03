from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.routers.summarize_router import router as summarize_router
from app.services.text.ai_summarize_service import get_pipeline  # <-- ADD

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Summarization API (extractive + AI) using free CPU models.",
)

setup_cors(app)

@app.on_event("startup")
async def warmup_model():
    """
    Preload the summarization model on startup to avoid cold start delay.
    """
    try:
        summarizer, _ = get_pipeline()
        summarizer("Warm-up inference to cache model weights.", min_length=5, max_length=15)
        print("✅ Model warmup completed successfully.")
    except Exception as e:
        print(f"⚠️ Warmup failed: {e}")

@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}

app.include_router(summarize_router)