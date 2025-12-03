"""
Public HTTP routes for transcription.

- /transcribe/video  -> accept MP4, return verbatim transcript (and optional AI summary)
"""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status

from app.schemas.transcribe import (
    TranscribeVideoOut,
    TranscribeVideoQuery,
    TranscribeAudioOut,
    TranscribeAudioQuery,
)
from app.controllers.transcribe_controller import (
    transcribe_video_action,
    transcribe_audio_action,
)


router = APIRouter(prefix="/transcribe", tags=["transcribe"])


@router.post("/video", response_model=TranscribeVideoOut, status_code=status.HTTP_200_OK)
async def transcribe_video(
    file: UploadFile = File(..., description="MP4 video file to be transcribed."),
    q: TranscribeVideoQuery = Depends(),
):
    """
    Transcribe an MP4 file:

    - Extracts audio via ffmpeg (mono 16k WAV).
    - Uses open-source Whisper (CPU) for verbatim transcription (keeps original language).
    - Optionally produces an abstractive summary using the local DistilBART model.

    Notes:
    - This endpoint does NOT require any paid external services.
    - Large files will take longer on CPU; consider chunking or client-side trimming if needed.
    """
    if file.content_type not in ("video/mp4", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type. Please upload an MP4 file.",
        )

    return transcribe_video_action(
        file=file,
        do_summary=q.do_summary,
        min_length=q.min_length,
        max_length=q.max_length,
    )


@router.post("/audio", response_model=TranscribeAudioOut, status_code=status.HTTP_200_OK)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file (e.g. MP3) to be transcribed."),
    q: TranscribeAudioQuery = Depends(),
):
    """
    Transcribe an audio file (e.g. MP3) and optionally summarize it.

    - Uses Whisper (CPU-only) for transcription.
    - Keeps the original language.
    - Optional abstractive summary powered by the local summarization model.
    """
    if not (file.content_type or "").lower().startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported content type. Please upload a valid audio file.",
        )

    return transcribe_audio_action(
        file=file,
        do_summary=q.do_summary,
        min_length=q.min_length,
        max_length=q.max_length,
    )