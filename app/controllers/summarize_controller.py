"""
Controllers orchestrate endpoint-level behavior:
- Validate guardrails (length, payload constraints)
- Call services
- Map service results to response schemas
"""

from fastapi import HTTPException

from app.schemas.summarize import (
    SummarizeIn,
    SummarizeOut,
    SummarizeAIIn,
    SummarizeAIOut,
)
from app.services.text.summarize_service import extractive_summary
from app.services.text.ai_summarize_service import summarize_ai_text

# Global guardrail to prevent abuse and control latency.
MAX_CHARS = 20000


def summarize_action(payload: SummarizeIn) -> SummarizeOut:
    """
    Extractive summarization controller.
    """
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


def summarize_ai_action(payload: SummarizeAIIn) -> SummarizeAIOut:
    """
    Abstractive (AI) summarization controller using free DistilBART.
    """
    text = payload.text.strip()
    if len(text) < 50:
        raise HTTPException(status_code=400, detail="Text is too short (>= 50 chars required).")
    if len(text) > MAX_CHARS:
        raise HTTPException(status_code=413, detail=f"Text exceeds {MAX_CHARS} characters.")

    summary = summarize_ai_text(
        text,
        min_length=payload.min_length,
        max_length=payload.max_length,
    )
    if not summary:
        raise HTTPException(status_code=422, detail="Unable to produce an AI summary.")

    return SummarizeAIOut(
        summary=summary,
        model_used="sshleifer/distilbart-cnn-12-6",
        min_length=payload.min_length,
        max_length=payload.max_length,
    )