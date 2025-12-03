# app/controllers/transcribe_controller.py

"""
Controller for transcription workflows.

- Accepts an MP4 upload.
- Extracts audio (WAV) via ffmpeg.
- Transcribes verbatim with Whisper (CPU).
- Optionally summarizes the transcript using the local summarization pipeline.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.services.media.video_audio_service import extract_wav_from_mp4
from app.services.speech.asr_service import transcribe_wav, DEFAULT_WHISPER_MODEL
from app.services.text.ai_summarize_service import summarize_ai_text

# Max duration safeguard for cheap tiers (in seconds).
# Puedes ajustar el valor sin tocar código, solo cambiando la variable en Railway.
MAX_VIDEO_DURATION_SECONDS = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "600"))  # 10 minutos por defecto
MAX_AUDIO_DURATION_SECONDS = int(os.getenv("MAX_AUDIO_DURATION_SECONDS", "900"))   # 15 min
SUMMARY_MODEL_ID = os.getenv("AI_SUMMARY_MODEL", "t5-small")

def transcribe_video_action(
    file: UploadFile,
    do_summary: bool,
    min_length: int,
    max_length: int,
) -> dict:
    """
    Orchestrate video transcription:
      1) Persist MP4 to a temp file.
      2) Extract WAV (mono/16k).
      3) Transcribe with Whisper (verbatim).
      4) Optionally summarize.

    Returns:
        dict payload matching TranscribeVideoOut schema.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        mp4_path = tmpdir_path / "input.mp4"

        # 1) Save uploaded file
        with mp4_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2) Extract WAV using ffmpeg
        wav_path = tmpdir_path / "audio.wav"
        wav_path, duration_seconds = extract_wav_from_mp4(mp4_path, wav_path)

        # 2.1) Duration guard to avoid timeouts in production
        if duration_seconds and duration_seconds > MAX_VIDEO_DURATION_SECONDS:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Video too long (~{int(duration_seconds)}s). "
                    f"Max allowed is {MAX_VIDEO_DURATION_SECONDS} seconds for this plan."
                ),
            )

        # 3) Transcribe WAV (auto language detect)
        transcript, language, _raw = transcribe_wav(wav_path)

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail="No speech detected in the provided video.",
            )

        # 4) Optional abstractive summary
        summary_text = None
        summary_model_id = None
        if do_summary:
            summary_text = summarize_ai_text(
                transcript,
                min_length=min_length,
                max_length=max_length,
            )
            # Ajusta al modelo real que estés usando internamente
            summary_model_id = "t5-small"

        return {
            "language": language,
            "duration_seconds": float(duration_seconds),
            "transcript": transcript,
            "summary": summary_text,
            "asr_model_used": f"whisper-{DEFAULT_WHISPER_MODEL}-cpu",
            "summary_model_used": summary_model_id,
        }


# ---------------------------
# Audio transcription (MP3, etc)
# ---------------------------

def transcribe_audio_action(
    file: UploadFile,
    do_summary: bool,
    min_length: int,
    max_length: int,
) -> dict:
    """
    Transcribe an audio file (e.g. MP3) and optionally summarize it.

    Steps:
      1) Save the uploaded audio file to a temp path.
      2) Run Whisper (CPU) directly on the file.
      3) Optionally generate an abstractive summary.

    Notes:
      - Only open-source components are used.
      - Works with common formats supported by Whisper (mp3, wav, m4a, etc).
    """
    if not file:
        raise HTTPException(status_code=400, detail="File is required.")

    content_type = (file.content_type or "").lower()
    if not content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported content type. Please upload an audio file (e.g. MP3).",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        ext = Path(file.filename or "").suffix or ".mp3"
        audio_path = tmpdir_path / f"input{ext}"

        # 1) Save uploaded audio
        with audio_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2) Transcribe using Whisper
        transcript, language, raw = transcribe_wav(audio_path)

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail="No speech detected in the provided audio file.",
            )

        # 2.1) Estimate duration from segments (best-effort)
        duration_seconds = 0.0
        segments = (raw or {}).get("segments") or []
        if segments:
            end = segments[-1].get("end")
            if isinstance(end, (int, float)):
                duration_seconds = float(end)

        if duration_seconds and duration_seconds > MAX_AUDIO_DURATION_SECONDS:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Audio too long (~{int(duration_seconds)}s). "
                    f"Max allowed is {MAX_AUDIO_DURATION_SECONDS} seconds."
                ),
            )

        # 3) Optional summary
        summary_text = None
        summary_model_id = None
        if do_summary:
            summary_text = summarize_ai_text(
                transcript,
                min_length=min_length,
                max_length=max_length,
            )
            summary_model_id = SUMMARY_MODEL_ID

        return {
            "language": language,
            "duration_seconds": float(duration_seconds),
            "transcript": transcript,
            "summary": summary_text,
            "asr_model_used": f"whisper-{DEFAULT_WHISPER_MODEL}-cpu",
            "summary_model_used": summary_model_id,
        }