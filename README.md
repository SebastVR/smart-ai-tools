# Smart AI Tools 🧠

A collection of lightweight, production-ready AI utilities powered by open-source models.

## Current Modules
- 📝 **Summarizer API** – Extractive and abstractive summarization using Hugging Face models.
- (coming soon) **Keyword Extractor**
- (coming soon) **PDF Summarizer**
- (coming soon) **Transcriber**

## Quick Start
```bash
docker build -t smart-ai-tools:latest .
docker run --rm -p 8000:8000 smart-ai-tools:latest

A production-ready **summarization API** with two endpoints:
- **Extractive** summarization (lightweight heuristic).
- **Abstractive (AI)** summarization using a **free**, **CPU-friendly** Hugging Face model:
  - Model: `sshleifer/distilbart-cnn-12-6` (DistilBART).

No paid LLMs, no GPU required. Designed for **Railway** deployment and **RapidAPI** monetization.

---

## Features

- `POST /summarize` — Extractive heuristic (no heavy models).
- `POST /summarize/ai` — Abstractive AI via DistilBART (free, CPU).
- CORS enabled (adjust in production).
- Clear Pydantic schemas and modular architecture (routers/controllers/services).

---

## Tech Stack

- FastAPI, Uvicorn
- Transformers, Torch (CPU)
- Python 3.12, Docker

---

## Endpoints

### Health
`GET /health`

**Response**
```json
{ "status": "ok" }