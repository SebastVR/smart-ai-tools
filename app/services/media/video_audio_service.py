"""
Media utilities for handling video/audio operations.

- Extract audio (WAV) from an MP4 file using ffmpeg binary (installed in the Docker image).
- Keep it minimal and CPU-friendly.

This module does NOT require any paid services.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple


def extract_wav_from_mp4(
    mp4_path: Path, wav_path: Path, sample_rate: int = 16000, channels: int = 1
) -> Tuple[Path, float]:
    """
    Extract mono WAV audio from an MP4 file using ffmpeg.

    Args:
        mp4_path: Path to the input MP4 file.
        wav_path: Path to the output WAV file.
        sample_rate: Target sample rate in Hz (default 16k).
        channels: Target number of channels (default mono = 1).

    Returns:
        (wav_path, duration_seconds)

    Raises:
        RuntimeError: if ffmpeg returns a non-zero exit code.
    """
    mp4_path = mp4_path.resolve()
    wav_path = wav_path.resolve()

    # 1) Extract WAV
    cmd = [
        "ffmpeg",
        "-y",                # overwrite
        "-i", str(mp4_path), # input
        "-ac", str(channels),
        "-ar", str(sample_rate),
        "-vn",               # no video
        "-f", "wav",
        str(wav_path),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed extracting audio: {proc.stderr.decode('utf-8', errors='ignore')}")

    # 2) Probe duration using ffprobe (avoid importing heavy libs)
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1",
        str(wav_path),
    ]
    probe = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if probe.returncode != 0:
        # Fallback: return unknown duration as 0.0 if probing fails
        return wav_path, 0.0

    try:
        duration = float(probe.stdout.decode().strip())
    except Exception:
        duration = 0.0

    return wav_path, duration