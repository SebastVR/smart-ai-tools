# CPU-only, free stack
FROM python:3.12-slim

# System deps: CA certs (HTTPS), curl/git (debug), build-essential (wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git build-essential \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face model into the image (no runtime downloads)
ENV HF_HOME=/root/.cache/huggingface
ENV MODEL_ID=sshleifer/distilbart-cnn-12-6
ENV MODEL_DIR=/models/distilbart-cnn-12-6

RUN python - <<'PY'
from huggingface_hub import snapshot_download
import os
model_id = os.environ.get("MODEL_ID")
local_dir = os.environ.get("MODEL_DIR")
snapshot_download(repo_id=model_id, local_dir=local_dir, local_dir_use_symlinks=False)
print(f"Downloaded model '{model_id}' to '{local_dir}'")
PY

# Copy the application
COPY . .

# Tell the app to use local model path
ENV AI_SUMMARY_MODEL_PATH=/models/distilbart-cnn-12-6

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]