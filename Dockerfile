# ---------------------------
#  Dockerfile - Smart AI Tools
#  Optimized for Railway (CPU)
# ---------------------------

FROM python:3.12-slim

# Environment setup
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    HF_HUB_DISABLE_TELEMETRY=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git build-essential && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the Hugging Face model
ENV MODEL_ID=sshleifer/distilbart-cnn-12-6
ENV MODEL_DIR=/models/distilbart-cnn-12-6
RUN python - <<'PY'
from transformers import pipeline
import os
os.environ["HF_HOME"] = "/root/.cache/huggingface"
pipe = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
pipe("Warm cache.", min_length=5, max_length=10, do_sample=False)
print("✅ Model preloaded successfully.")
PY

# Copy app
COPY . .

# Local model reference
ENV AI_SUMMARY_MODEL_PATH=/models/distilbart-cnn-12-6

EXPOSE 8000

# Run app (bind to dynamic $PORT for Railway)
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]