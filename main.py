"""
Smart AI Tools - Main Application
---------------------------------
- /health           : Health check
- /summarize        : Extractive summarization
- /summarize/ai     : Abstractive summarization (DistilBART, CPU-only)
"""

from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from app.core.config import settings
from app.core.cors import setup_cors
from app.routers.summarize_router import router as summarize_router
from app.services.text.ai_summarize_service import get_pipeline

# Background executor to run warmup asynchronously
_executor = ThreadPoolExecutor(max_workers=1)


def _do_warmup():
    """
    Perform background model warmup (non-blocking).
    """
    try:
        summarizer, _ = get_pipeline()
        summarizer("Warm-up.", min_length=5, max_length=10, do_sample=False)
        print("✅ Model warmup completed successfully (background).")
    except Exception as e:
        print(f"⚠️ Warmup failed (background): {e}")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Summarization API (extractive + AI) using free CPU models.",
)

# Enable CORS
setup_cors(app)


@app.on_event("startup")
def schedule_warmup():
    """
    Schedule model warmup in background.
    """
    _executor.submit(_do_warmup)
    print("↗️ Warmup scheduled in background.")


@app.get("/health")
def health() -> dict:
    """Simple health check."""
    return {"status": "ok"}


# Register routes
app.include_router(summarize_router)