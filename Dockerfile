# ---------------------------
#  Dockerfile - Smart AI Tools
#  Optimized for Railway (CPU)
# ---------------------------
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    HF_HUB_DISABLE_TELEMETRY=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git build-essential ffmpeg && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python - <<'PY'
import whisper
from transformers import pipeline
print("✅ Sanity check OK")
print("   - whisper import OK")
print("   - transformers pipeline import OK")
PY

# --- Pre-cache summarization model (ligero, OK) ---
ENV AI_SUMMARY_MODEL=t5-small
RUN python - <<'PY'
from transformers import pipeline
pipe = pipeline("summarization", model="t5-small")
pipe("summarize: Warm cache.", min_length=5, max_length=10, do_sample=False)
print("✅ Summarization model (t5-small) preloaded successfully.")
PY

# --- Whisper config: solo elegimos modelo, SIN precargar en build ---
# tiny es mucho más amigable para CPU/Railway que small
ENV WHISPER_MODEL=tiny

# Código de la app
COPY . .

EXPOSE 8000

CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]