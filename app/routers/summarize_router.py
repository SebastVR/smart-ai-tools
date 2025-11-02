"""
Routers define public HTTP routes and delegate to controllers.
"""

from fastapi import APIRouter
from app.schemas.summarize import (
    SummarizeIn, SummarizeOut,
    SummarizeAIIn, SummarizeAIOut,
)
from app.controllers.summarize_controller import (
    summarize_action,
    summarize_ai_action,
)

router = APIRouter(prefix="/summarize", tags=["summarizer"])


@router.post("", response_model=SummarizeOut)
def summarize(payload: SummarizeIn):
    """
    Extractive summarization endpoint (heuristic).
    """
    return summarize_action(payload)


@router.post("/ai", response_model=SummarizeAIOut)
def summarize_ai(payload: SummarizeAIIn):
    """
    Abstractive summarization endpoint (free DistilBART model on CPU).
    """
    return summarize_ai_action(payload)