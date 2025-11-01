from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SummarizeIn, SummarizeOut
from app.summarizer import extractive_summary

app = FastAPI(
    title="Smart Summarizer PRO API",
    version="1.0.0",
    description="Lightweight extractive summarization API (no paid external models).",
)

# Open CORS for convenience; tighten to specific domains in production if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic guardrail to prevent abuse and control latency.
MAX_CHARS = 20000

@app.get("/health")
def health():
    """Healthcheck endpoint."""
    return {"status": "ok"}

@app.post("/summarize", response_model=SummarizeOut)
def summarize(payload: SummarizeIn):
    """Summarize a given text using a simple extractive heuristic."""
    text = payload.text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text is too short (>= 50 chars required).")
    if len(text) > MAX_CHARS:
        raise HTTPException(status_code=413, detail=f"Text exceeds {MAX_CHARS} characters.")

    chosen, total = extractive_summary(text, payload.ratio, payload.max_sentences)
    if not chosen:
        raise HTTPException(status_code=422, detail="Unable to produce a summary.")

    return SummarizeOut(
        sentences=chosen,
        summary=" ".join(chosen),
        ratio_used=payload.ratio,
        total_sentences=total,
    )