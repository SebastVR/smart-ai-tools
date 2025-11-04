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

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates git build-essential && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Opcional) Pre-cache model during build to avoid network on first run
# Si el plan de Railway es muy chico, puedes comentar todo este bloque.
ENV MODEL_ID=t5-small
RUN python - <<'PY'
from transformers import pipeline
pipe = pipeline("summarization", model="t5-small")
pipe("summarize: Warm cache.", min_length=5, max_length=10, do_sample=False)
print("✅ t5-small preloaded successfully at build time.")
PY

# Copy app
COPY . .

# (Opcional) si usas una ruta local de modelo; si no, se tomará desde HF_HOME cache
# ENV AI_SUMMARY_MODEL_PATH=/models/distilbart-cnn-12-6

EXPOSE 8000

# Bind Uvicorn to Railway dynamic PORT (fallback 8000 for local)
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]