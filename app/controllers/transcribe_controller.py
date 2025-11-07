"""
Controller for transcription workflows.

- Accepts an MP4 upload.
- Extracts audio (WAV) via ffmpeg.
- Transcribes verbatim with Whisper (CPU).
- Optionally summarizes the transcript using the local DistilBART pipeline.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import UploadFile

from app.services.media.video_audio_service import extract_wav_from_mp4
from app.services.speech.asr_service import transcribe_wav, DEFAULT_WHISPER_MODEL
from app.services.text.ai_summarize_service import summarize_ai_text


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
      4) Optionally summarize with DistilBART.

    Returns:
        dict payload matching TranscribeVideoOut schema.
    """
    # 1) Save the uploaded MP4 into a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        mp4_path = tmpdir_path / "input.mp4"
        with mp4_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2) Extract WAV using ffmpeg
        wav_path = tmpdir_path / "audio.wav"
        wav_path, duration_seconds = extract_wav_from_mp4(mp4_path, wav_path)

        # 3) Transcribe WAV (auto language detect)
        transcript, language, _raw = transcribe_wav(wav_path)

        # 4) Optional abstractive summary using existing local model
        summary_text = None
        summary_model_id = None
        if do_summary:
            summary_text = summarize_ai_text(
                transcript,
                min_length=min_length,
                max_length=max_length,
            )
            summary_model_id = "sshleifer/distilbart-cnn-12-6"

        return {
            "language": language,
            "duration_seconds": float(duration_seconds),
            "transcript": transcript,
            "summary": summary_text,
            "asr_model_used": f"whisper-{DEFAULT_WHISPER_MODEL}-cpu",
            "summary_model_used": summary_model_id,
        }