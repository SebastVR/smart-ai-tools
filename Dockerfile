# ---------------------------
#  Dockerfile - Smart AI Tools
#  Optimized for Railway (CPU)
# ---------------------------
FROM python:3.12-slim

# Keep memory footprint low and predictable
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    HF_HUB_DISABLE_TELEMETRY=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

# System dependencies:
# - ffmpeg: needed to extract/decode audio (Whisper).
# - build-essential: helps build any wheel if needed on slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git build-essential ffmpeg && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------------------------
# Python dependencies
# (Your requirements.txt already includes openai-whisper==20250625)
# ---------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python - <<'PY'
import sys
import whisper
from transformers import pipeline
print("✅ Sanity check OK")
print("   - whisper:", getattr(whisper, "__version__", "unknown"))
print("   - transformers pipeline import OK")
PY

# ---------------------------
# Pre-cache summarization model (CPU-only, open source)
# Align with AI_SUMMARY_MODEL used by your service (t5-small by default).
# ---------------------------
ENV AI_SUMMARY_MODEL=t5-small
RUN python - <<'PY'
from transformers import pipeline
pipe = pipeline("summarization", model="t5-small")
# "t5-small" expects the "summarize: " prefix to engage summarization task
pipe("summarize: Warm cache.", min_length=5, max_length=10, do_sample=False)
print("✅ Summarization model (t5-small) preloaded successfully at build time.")
PY

# ---------------------------
# (Optional) Pre-cache Whisper model so there is no runtime download
# If your build environment has low RAM/CPU, you can comment this block.
# ---------------------------
ENV WHISPER_MODEL=small
RUN python - <<'PY'
import os, whisper
model_id = os.environ.get("WHISPER_MODEL", "small")
# This downloads the model weights into ~/.cache if not present
whisper.load_model(model_id, device="cpu")
print(f"✅ Whisper model '{model_id}' preloaded successfully at build time.")
PY

# ---------------------------
# Copy application code
# ---------------------------
COPY . .

# Expose port (Railway sets $PORT; fallback 8000 for local)
EXPOSE 8000

# Start Uvicorn (bind to dynamic $PORT on Railway)
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]