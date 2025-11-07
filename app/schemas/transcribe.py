"""
Pydantic models for transcription endpoints (video/audio).
All docstrings and field descriptions are in English as requested.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TranscribeVideoQuery(BaseModel):
    """
    Optional query parameters to control summarization behavior for video transcription.
    """
    do_summary: bool = Field(
        default=True,
        description="If true, the API will also produce an abstractive summary using the local AI model.",
    )
    min_length: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Minimum token length for the abstractive summary.",
    )
    max_length: int = Field(
        default=160,
        ge=20,
        le=600,
        description="Maximum token length for the abstractive summary.",
    )


class TranscribeVideoOut(BaseModel):
    """
    Response for /transcribe/video.
    """
    language: str = Field(..., description="Auto-detected language code (e.g., 'en', 'es').")
    duration_seconds: float = Field(..., description="Approximate audio duration in seconds.")
    transcript: str = Field(..., description="Full verbatim transcript in the original language.")
    summary: Optional[str] = Field(
        default=None,
        description="Abstractive summary generated with the local AI model (if do_summary=true).",
    )
    asr_model_used: str = Field(..., description="Identifier of the speech-to-text model used.")
    summary_model_used: Optional[str] = Field(
        default=None, description="Identifier of the summarization model used (if do_summary=true)."
    )