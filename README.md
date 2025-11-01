# Smart Summarizer PRO API

A lightweight extractive summarization API built with FastAPI. No external paid models required.

## Endpoints
- `GET /health` -> `{"status":"ok"}`
- `POST /summarize`
  **Request body:**
  ```json
  {
    "text": "Long text goes here ...",
    "ratio": 0.2,
    "max_sentences": 8
  }