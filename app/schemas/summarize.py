"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- Extractive (heuristic) ----------
class SummarizeIn(BaseModel):
    """
    Request schema for the extractive summarization endpoint.
    """
    text: str = Field(..., min_length=50, description="Text to summarize (>= 50 chars).")
    ratio: float = Field(0.2, ge=0.05, le=0.6, description="Summary ratio (5% - 60%).")
    max_sentences: Optional[int] = Field(None, ge=1, le=25, description="Optional cap on sentence count.")


class SummarizeOut(BaseModel):
    """
    Response schema for the extractive summarization endpoint.
    """
    sentences: List[str]
    summary: str
    ratio_used: float
    total_sentences: int


# ---------- Abstractive (AI: DistilBART) ----------
class SummarizeAIIn(BaseModel):
    """
    Request schema for AI-based abstractive summarization.
    """
    text: str = Field(..., min_length=50, description="Text to summarize (>= 50 chars).")
    min_length: int = Field(60, ge=20, le=300, description="Lower bound for the generated summary length.")
    max_length: int = Field(160, ge=60, le=400, description="Upper bound for the generated summary length.")


class SummarizeAIOut(BaseModel):
    """
    Response schema for AI-based abstractive summarization.
    """
    summary: str
    model_used: str
    min_length: int
    max_length: int