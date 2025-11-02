"""
Abstractive summarization using a free, CPU-friendly model:
- Default model: sshleifer/distilbart-cnn-12-6 (DistilBART)
- Uses local model path if available (baked into the Docker image)
- CPU-only inference (device=-1)
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

DEFAULT_MODEL = os.getenv("AI_SUMMARY_MODEL", "sshleifer/distilbart-cnn-12-6")
LOCAL_MODEL_PATH = os.getenv("AI_SUMMARY_MODEL_PATH")  # e.g., /models/distilbart-cnn-12-6
MODEL_SOURCE = LOCAL_MODEL_PATH if (LOCAL_MODEL_PATH and os.path.isdir(LOCAL_MODEL_PATH)) else DEFAULT_MODEL

MAX_INPUT_TOKENS = int(os.getenv("AI_SUMMARY_MAX_INPUT_TOKENS", "900"))
CHUNK_OVERLAP_SENTENCES = int(os.getenv("AI_SUMMARY_SENT_OVERLAP", "1"))


@lru_cache(maxsize=1)
def get_pipeline():
    """
    Lazily load and cache the summarization pipeline.
    Prioritize local model directory to avoid network at runtime.
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SOURCE)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_SOURCE)
    summarizer = pipeline(
        "summarization",
        model=model,
        tokenizer=tokenizer,
        framework="pt",
        device=-1,  # CPU
    )
    return summarizer, tokenizer


def _naive_sentence_split(text: str) -> List[str]:
    """Minimal sentence segmentation by punctuation."""
    import re
    _SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')
    parts = _SENT_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _split_into_token_chunks(text: str, max_tokens: int) -> List[str]:
    """
    Split text into token-aware chunks using the model tokenizer.
    Keeps a small sentence overlap between chunks to preserve context.
    """
    summarizer, tokenizer = get_pipeline()
    sentences = _naive_sentence_split(text)
    chunks: List[str] = []

    current: List[str] = []
    current_len = 0

    def tokens_count(s: str) -> int:
        return len(tokenizer.encode(s, add_special_tokens=False))

    for s in sentences:
        s_len = tokens_count(s)
        if s_len > max_tokens:
            # Hard-split a single long sentence by tokens
            hard_tokens = tokenizer.encode(s, add_special_tokens=False)
            for j in range(0, len(hard_tokens), max_tokens):
                piece = tokenizer.decode(hard_tokens[j:j + max_tokens], skip_special_tokens=True)
                chunks.append(piece.strip())
            current, current_len = [], 0
            continue

        if current_len + s_len <= max_tokens:
            current.append(s)
            current_len += s_len
        else:
            if current:
                chunks.append(" ".join(current).strip())
            overlap = current[-CHUNK_OVERLAP_SENTENCES:] if CHUNK_OVERLAP_SENTENCES and current else []
            current = overlap + [s] if overlap else [s]
            current_len = sum(tokens_count(x) for x in current)

    if current:
        chunks.append(" ".join(current).strip())

    return chunks


def _summarize_block(block: str, min_length: int, max_length: int) -> str:
    """Summarize a single chunk using the pipeline."""
    summarizer, _ = get_pipeline()
    out = summarizer(
        block,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,
        truncation=True,
    )[0]["summary_text"]
    return out.strip()


def summarize_ai_text(
    text: str,
    min_length: int = 60,
    max_length: int = 160,
) -> str:
    """
    Map-Reduce summarization:
      1) Token-aware chunking.
      2) Summarize each chunk.
      3) Summarize the concatenated partials.
    """
    text = text.strip()
    if not text:
        return ""

    chunks = _split_into_token_chunks(text, MAX_INPUT_TOKENS)

    if len(chunks) == 1:
        return _summarize_block(chunks[0], min_length, max_length)

    partials = [_summarize_block(c, max(20, min_length // 2), max_length) for c in chunks]
    combined = " ".join(partials)
    final = _summarize_block(combined, min_length, max_length)
    return final