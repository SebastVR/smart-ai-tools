"""
Speech-to-text (ASR) service using open-source Whisper (CPU-friendly).

- Package: open-source `whisper` (a.k.a. openai-whisper) under MIT License.
- Runs fully on CPU; no external paid services.
- Auto-detects language; returns verbatim transcript.

Environment variables:
- WHISPER_MODEL (default: "small")   # other options: "base", "medium" (larger = slower)
- WHISPER_COMPUTE_TYPE ignored for openai-whisper; used by faster-whisper only.

Note: We deliberately use openai-whisper since torch is already in your stack.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Tuple

import whisper  # open-source speech-to-text


DEFAULT_WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")


@lru_cache(maxsize=1)
def get_asr_model():
    """
    Lazily load and cache the Whisper model in CPU mode.
    """
    model = whisper.load_model(DEFAULT_WHISPER_MODEL, device="cpu")
    return model


def transcribe_wav(wav_path: Path) -> Tuple[str, str, Dict[str, Any]]:
    """
    Transcribe a WAV file (mono 16k recommended) and return the verbatim text,
    the detected language code, and raw info dict.

    Args:
        wav_path: path to a WAV audio file.

    Returns:
        transcript_text, language_code, raw_info
    """
    model = get_asr_model()
    # `translate=False` keeps the original language; automatic language detection is included.
    result = model.transcribe(str(wav_path), task="transcribe", verbose=False, fp16=False)
    text = (result.get("text") or "").strip()
    lang = result.get("language") or "unknown"
    return text, lang, result